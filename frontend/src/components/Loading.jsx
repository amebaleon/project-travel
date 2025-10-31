import React from 'react';
import { Player } from '@lottiefiles/react-lottie-player';

const Loading = () => {
  return (
    <div className="loading-overlay">
      <Player
        src="https://lottie.host/b1b9c6e3-1b9b-4b9c-8d5a-3e8b3b1b1b1b/lottie.json"
        className="player"
        loop
        autoplay
        style={{ height: '300px', width: '300px' }}
      />
    </div>
  );
};

export default Loading;