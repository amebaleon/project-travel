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
      <BackgroundSlider />
    </div>
  );
}
