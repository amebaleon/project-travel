import React, { useEffect, useRef, useState } from "react";
import "./BackgroundSlider.css";
import HeroText from "./HeroText";

export default function BackgroundSlider({ onOpenInput }) {
  // 배경 이미지 순서 (서울 -> 부산 -> 전주 -> 제주)
  const images = ["/서울.png", "/부산.jpg", "/전주.png", "/제주.jpg"];
  const captions = ["서울", "부산", "전주", "제주"];
  // 각 이미지에 맞춘 텍스트 색(필요하면 조정 가능)
  // 주: 사용자가 준 #151B54는 부산 이미지에 맞춘 색입니다.
  // 전주 색상 변경: 따뜻하고 자연스러운 톤으로 조정 (index 2)
  const textColors = ["#2b2b2b", "#151B54", "#A0522D", "#0e5a3c"];
  const [textColor, setTextColor] = useState(textColors[0]);
  const textColorRef = useRef(textColors[0]);

  // 현재 인덱스
  const [current, setCurrent] = useState(0);
  const currentRef = useRef(0);
  // 두 레이어 중 어떤 레이어가 전면인지 (0 또는 1)
  const [front, setFront] = useState(0);
  const frontRef = useRef(0);
  // 각 레이어의 src
  const [layers, setLayers] = useState([images[0], ""]);
  const layersRef = useRef([images[0], ""]);
  // 전환 중인지 플래그
  const [isTransitioning, setIsTransitioning] = useState(false);

  // 전환 시간(ms)과 간격(ms)
  const TRANS_MS = 900; // 충분히 길게 하여 깜빡임 제거
  const GAP_MS = 3600;

  const timerRef = useRef(null);
  // 레이어 DOM 참조 배열
  const layerRefs = useRef([null, null]);

  useEffect(() => {
    // 자동 전환 시작
    timerRef.current = setInterval(() => {
      goNext();
    }, GAP_MS);
    return () => clearInterval(timerRef.current);
    // current를 의존성에 넣지 않음: 내부에서 항상 최신을 계산
  }, []);

  // 다음 이미지로 이동하는 함수 (겹쳐서 부드럽게 전환)
  const goNext = () => {
    if (isTransitioning) return; // 이미 전환 중이면 무시
    const cur = currentRef.current;
    const next = (cur + 1) % images.length;

    // backLayer에 다음 이미지 세팅
    const back = frontRef.current ^ 1; // 반대 레이어 인덱스
    const newLayers = [...layersRef.current];
    // 먼저 layers 상태와 ref에 next 이미지 할당
    newLayers[back] = images[next];
    layersRef.current = newLayers;
    setLayers(newLayers);

    // 트랜지션 플래그 세팅
    setIsTransitioning(true);

    // back 요소가 로드될 때까지 기다림(로딩 중 흰 배경 표시 방지)
    const backEl = layerRefs.current[back];
    const doTransition = () => {
      // 부드러운 색상 전환 시작: 텍스트 색을 먼저 변경하면 CSS transition으로 자연스럽게 페이드합니다.
      const targetColor = textColors[next] || "#151B54";
      setTextColor(targetColor);
      textColorRef.current = targetColor;
      // 프레임 기반 애니메이션으로 전환 (sum of opacities = 1 유지)
      const frontEl = layerRefs.current[frontRef.current];
      const backEl2 = layerRefs.current[back];
      if (!frontEl || !backEl2) {
        // 안전하게 즉시 교체
        setCurrent(next);
        currentRef.current = next;
        setFront(back);
        frontRef.current = back;
        setIsTransitioning(false);
        return;
      }

      // 초기 스타일 설정
      backEl2.style.transition = "none";
      frontEl.style.transition = "none";
      backEl2.style.opacity = "0";
      frontEl.style.opacity = "1";

      const start = performance.now();
      const step = (now) => {
        const elapsed = now - start;
        const t = Math.min(1, elapsed / TRANS_MS);
        // 항상 두 opacity의 합이 1이 되도록 설정
        frontEl.style.opacity = String(1 - t);
        backEl2.style.opacity = String(t);
        if (t < 1) {
          requestAnimationFrame(step);
        } else {
          // 애니메이션 종료 후 정리
          // front 상태를 back으로 교체
          setCurrent(next);
          currentRef.current = next;
          setFront(back);
          frontRef.current = back;
          // 이전 레이어의 src는 비워서 메모리 최적화
          const cleared = [...layersRef.current];
          cleared[frontRef.current ^ 1] = ""; // clear the other layer (previous front)
          layersRef.current = cleared;
          setLayers(cleared);
          setIsTransitioning(false);
        }
      };
      requestAnimationFrame(step);
    };

    if (backEl) {
      // 캐시되어 있으면 바로 전환
      if (backEl.complete && backEl.naturalWidth !== 0) {
        doTransition();
      } else {
        // 로드 이벤트로 전환 시작
        const onLoad = () => {
          backEl.removeEventListener("load", onLoad);
          doTransition();
        };
        backEl.addEventListener("load", onLoad);
      }
    } else {
      // ref가 아직 없으면 안전하게 바로 전환
      // 즉시 교체 전에도 텍스트 색을 맞춤
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
      {/* 전체 화면 뒤에 고정된 배경 (레이아웃에 영향 없음) */}
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
        {/* 레이어 0 */}
        <img
          id="bg-layer-0"
          ref={(el) => (layerRefs.current[0] = el)}
          className={`bg-slider-layer ${front === 0 ? "front" : ""}`}
          src={layers[0] || images[0]}
          alt={captions[current]}
          style={{ transitionDuration: `${TRANS_MS}ms` }}
        />

        {/* 레이어 1 */}
        <img
          id="bg-layer-1"
          ref={(el) => (layerRefs.current[1] = el)}
          className={`bg-slider-layer ${front === 1 ? "front" : ""}`}
          src={layers[1] || images[0]}
          alt={captions[current]}
          style={{ transitionDuration: `${TRANS_MS}ms` }}
        />
      </div>

      {/* 오버레이 컨트롤 (배경 위) */}
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

      {/* 고정 텍스트 레이어: Your Korea, Designed by AI */}
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
            // 간단히 입력 화면 열기 동작을 재사용
            onOpenInput && onOpenInput();
          }}
        />
      </div>
    </>
  );
}
