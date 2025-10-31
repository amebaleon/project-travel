import React, { useState } from "react";

export default function HeroText({
  title = "Your Korea, Designed by AI",
  subtitle = "Make your trip easier",
  color = "#151B54",
  onGetStart,
}) {
  const [hover, setHover] = useState(false);
  return (
    <div
      style={{
        position: "absolute",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        background: "rgba(255, 255, 255, 0.2)",
        backdropFilter: "blur(10px) saturate(1.2)",
        borderRadius: "16px",
        border: "2px solid rgba(255, 255, 255, 0.5)",
        boxShadow: "0 8px 32px 0 rgba(31, 38, 135, 0.37)",
        padding: "32px",
        paddingTop: "60px",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        width: "500px",
        height: "350px",
        maxWidth: "90vw",
        maxHeight: "90vw",
      }}
    >
      <div
        style={{
          fontFamily: "Inter, 'Helvetica Neue', Arial, sans-serif",
          fontWeight: 700,
          fontSize: "clamp(28px, 4.5vw, 72px)",
          lineHeight: "1.05",
          letterSpacing: "0.2px",
          textAlign: "center",
          color: color,
          transition: "color 400ms ease",
          width: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          borderRadius: 0,
          opacity: 1,
          filter: "drop-shadow(0px 4px 4px rgba(0,0,0,0.25))",
          textShadow:
            "0 4px 8px rgba(0,0,0,0.45), 0 1px 0 rgba(255,255,255,0.03), 0 0 2px rgba(0,0,0,0.25)",
          WebkitTextStroke: "0.6px rgba(255,255,255,0.06)",
        }}
      >
        {title}
      </div>

      <div
        style={{
          marginTop: 12,
          fontFamily: "Inter, 'Helvetica Neue', Arial, sans-serif",
          fontWeight: 400,
          fontSize: 20,
          color: "#ffffff",
          textAlign: "center",
          width: "100%",
          lineHeight: 1.4,
          zIndex: 6,
        }}
      >
        {subtitle}
      </div>

      <div style={{ marginTop: 18 }}>
        <button
          onClick={() => onGetStart && onGetStart()}
          onMouseEnter={() => setHover(true)}
          onMouseLeave={() => setHover(false)}
          onFocus={() => setHover(true)}
          onBlur={() => setHover(false)}
          style={{
            background: hover ? "#ffffff" : "rgba(255,255,255,0.08)",
            color: hover ? color : "#ffffff",
            border: "2px solid rgba(255,255,255,0.9)",
            padding: "10px 18px",
            borderRadius: 8,
            fontWeight: 600,
            cursor: "pointer",
            boxShadow: hover
              ? "0 8px 20px rgba(0,0,0,0.25)"
              : "0 2px 6px rgba(0,0,0,0.12)",
            transform: hover ? "translateY(-2px) scale(1.02)" : "none",
            transition:
              "transform 160ms ease, box-shadow 160ms ease, background 160ms ease, color 160ms ease",
          }}
        >
          Get Started
        </button>
      </div>
    </div>
  );
}
