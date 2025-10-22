import React, { useEffect, useRef, useState } from "react";
import "./BackgroundSlider.css";
import HeroText from "./HeroText";

export default function BackgroundSlider({ onOpenInput }) {
  const images = ["/서울.png", "/부산.jpg", "/전주.png", "/제주.jpg"];
  const captions = ["서울", "부산", "전주", "제주"];
  const textColors = ["#2b2b2b", "#151B54", "#A0522D", "#0e5a3c"];
  const [textColor, setTextColor] = useState(textColors[0]);
  const textColorRef = useRef(textColors[0]);

  const [current, setCurrent] = useState(0);
  const currentRef = useRef(0);
  const [front, setFront] = useState(0);
  const frontRef = useRef(0);
  const [layers, setLayers] = useState([images[0], ""]);
  const layersRef = useRef([images[0], ""]);
  const [isTransitioning, setIsTransitioning] = useState(false);

  const TRANS_MS = 900;
  const GAP_MS = 3600;

  const timerRef = useRef(null);
  const layerRefs = useRef([null, null]);

  useEffect(() => {
    timerRef.current = setInterval(() => goNext(), GAP_MS);
    return () => clearInterval(timerRef.current);
  }, []);

  const goNext = () => {
    if (isTransitioning) return;
    const cur = currentRef.current;
    const next = (cur + 1) % images.length;

    const back = frontRef.current ^ 1;
    const newLayers = [...layersRef.current];
    newLayers[back] = images[next];
    layersRef.current = newLayers;
    setLayers(newLayers);

    setIsTransitioning(true);

    const backEl = layerRefs.current[back];
    const doTransition = () => {
      const targetColor = textColors[next] || "#151B54";
      setTextColor(targetColor);
      textColorRef.current = targetColor;

      const frontEl = layerRefs.current[frontRef.current];
      const backEl2 = layerRefs.current[back];
      if (!frontEl || !backEl2) {
        setCurrent(next);
        currentRef.current = next;
        setFront(back);
        frontRef.current = back;
        setIsTransitioning(false);
        return;
      }

      backEl2.style.transition = "none";
      frontEl.style.transition = "none";
      backEl2.style.opacity = "0";
      frontEl.style.opacity = "1";

      const start = performance.now();
      const step = (now) => {
        const elapsed = now - start;
        const t = Math.min(1, elapsed / TRANS_MS);
        frontEl.style.opacity = String(1 - t);
        backEl2.style.opacity = String(t);
        if (t < 1) {
          requestAnimationFrame(step);
        } else {
          setCurrent(next);
          currentRef.current = next;
          setFront(back);
          frontRef.current = back;
          const cleared = [...layersRef.current];
          cleared[frontRef.current ^ 1] = "";
          layersRef.current = cleared;
          setLayers(cleared);
          setIsTransitioning(false);
        }
      };
      requestAnimationFrame(step);
    };

    if (backEl) {
      if (backEl.complete && backEl.naturalWidth !== 0) {
        doTransition();
      } else {
        const onLoad = () => {
          backEl.removeEventListener("load", onLoad);
          doTransition();
        };
        backEl.addEventListener("load", onLoad);
      }
    } else {
      const targetColor = textColors[next] || "#151B54";
      setTextColor(targetColor);
      textColorRef.current = targetColor;
      doTransition();
    }
  };

  // 수동 버튼이 눌리면 자동 타이머 리셋
  const handleNext = () => {
    clearInterval(timerRef.current);
    goNext();
    timerRef.current = setInterval(() => goNext(), GAP_MS);
  };

  return (
    <>
      <div
        style={{
          position: "fixed",
          inset: 0,
          zIndex: -1,
          overflow: "hidden",
          pointerEvents: "none",
        }}
        aria-hidden
      >
        <img
          id="bg-layer-0"
          ref={(el) => (layerRefs.current[0] = el)}
          className={`bg-slider-layer ${front === 0 ? "front" : ""}`}
          src={layers[0] || images[0]}
          alt={captions[current]}
          style={{ transitionDuration: `${TRANS_MS}ms` }}
        />

        <img
          id="bg-layer-1"
          ref={(el) => (layerRefs.current[1] = el)}
          className={`bg-slider-layer ${front === 1 ? "front" : ""}`}
          src={layers[1] || images[0]}
          alt={captions[current]}
          style={{ transitionDuration: `${TRANS_MS}ms` }}
        />
      </div>

      <div
        style={{
          position: "relative",
          zIndex: 2,
          width: "100%",
          display: "flex",
          justifyContent: "center",
        }}
      >
        <div style={{ marginTop: 12, background: "transparent", padding: 8 }}>
          <button
            onClick={() => onOpenInput && onOpenInput()}
            style={{ marginRight: 8 }}
          >
            입력 화면으로 이동
          </button>
          <button onClick={handleNext}>다음</button>
        </div>
      </div>

      <div
        aria-hidden={false}
        style={{
          position: "fixed",
          left: 0,
          top: "var(--navbar-height)",
          width: "100vw",
          height: "calc(100vh - var(--navbar-height))",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          pointerEvents: "auto",
          zIndex: 5,
          padding: "20px",
          boxSizing: "border-box",
        }}
      >
        <HeroText
          title={"Your Korea, Designed by AI"}
          subtitle={"Make your trip easier"}
          color={textColor}
          onGetStart={() => {
            onOpenInput && onOpenInput();
          }}
        />
      </div>
    </>
  );
}
