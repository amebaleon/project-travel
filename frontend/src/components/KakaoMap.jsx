
import React, { useEffect, useRef } from 'react';

const KakaoMap = ({ recommendations }) => {
  const mapContainer = useRef(null);

  useEffect(() => {
    if (!recommendations || recommendations.length === 0) {
      return;
    }

    const locations = recommendations.flatMap(dailyPlan => dailyPlan.recommendations);

    if (locations.length === 0) {
      return;
    }

    const checkKakao = () => {
      if (window.kakao && window.kakao.maps) {
        const { kakao } = window;
        const options = {
          center: new kakao.maps.LatLng(locations[0].latitude, locations[0].longitude),
          level: 8,
        };
        const map = new kakao.maps.Map(mapContainer.current, options);

        locations.forEach(location => {
          const markerPosition = new kakao.maps.LatLng(location.latitude, location.longitude);

          const marker = new kakao.maps.Marker({
            position: markerPosition,
          });

          const content = `<div style="padding:5px;background-color:white;border:1px solid black;border-radius:5px;">${location.name}</div>`;

          const overlay = new kakao.maps.CustomOverlay({
            content: content,
            map: null,
            position: marker.getPosition(),
            yAnchor: 1.5
          });

          kakao.maps.event.addListener(marker, 'mouseover', function() {
            overlay.setMap(map);
          });

          kakao.maps.event.addListener(marker, 'mouseout', function() {
            overlay.setMap(null);
          });

          marker.setMap(map);
        });
      } else {
        setTimeout(checkKakao, 100);
      }
    };

    checkKakao();
  }, [recommendations]);

  return <div ref={mapContainer} style={{ width: '100%', height: '100vh' }} />;
};

export default KakaoMap;
