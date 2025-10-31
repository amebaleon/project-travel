import React, { useState } from "react";
import Navbar from "../components/Navbar";
import BackgroundSlider from "../components/BackgroundSlider";
import HeroText from "../components/HeroText";
import TravelInput from "../components/TravelInput";
import { useNavigate } from "react-router-dom";

const TRANSITION_DURATION = 500; // ms

export default function Home() {
  const [showInput, setShowInput] = useState(false);
  const [modalOpacity, setModalOpacity] = useState(0);
  const navigate = useNavigate();

  const handleGetStarted = () => {
    setShowInput(true);
    setTimeout(() => {
      setModalOpacity(1);
    }, 50);
  };

  const handleCloseModal = () => {
    setModalOpacity(0);
    setTimeout(() => {
      setShowInput(false);
    }, TRANSITION_DURATION);
  };

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      <Navbar />
      <BackgroundSlider />
      <div
        style={{
          flexGrow: 1, // This makes the div take up remaining vertical space
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center", // Vertically center content
          padding: "20px",
        }}
      >
        {!showInput && <HeroText onGetStart={handleGetStarted} />}
      </div>

      <div
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          backgroundColor: "rgba(0, 0, 0, 0.7)",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          zIndex: 1000,
          opacity: modalOpacity,
          transition: `opacity ${TRANSITION_DURATION}ms ease-in-out`,
          pointerEvents: showInput ? "auto" : "none",
          visibility: showInput ? "visible" : "hidden",
        }}
      >
        <TravelInput onClose={handleCloseModal} navigate={navigate} />
      </div>
    </div>
  );
}