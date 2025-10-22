import React, { useState } from "react";
import Navbar from "../components/Navbar";
import BackgroundSlider from "../components/BackgroundSlider";
import TravelInput from "../components/TravelInput";

export default function Home() {
  const [showInput, setShowInput] = useState(false);
  const [query, setQuery] = useState("");

  return (
    <div>
      <Navbar />
      <div style={{ position: "relative", zIndex: 3, padding: 20 }}>
        {showInput ? (
          <TravelInput
            query={query}
            setQuery={setQuery}
            onClose={() => setShowInput(false)}
          />
        ) : (
          <BackgroundSlider onOpenInput={() => setShowInput(true)} />
        )}
      </div>
    </div>
  );
}
