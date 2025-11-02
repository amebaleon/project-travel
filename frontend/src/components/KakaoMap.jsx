import React, { useEffect, useRef } from 'react';

function KakaoMap({ recommendations, centerLocation }) {
  const mapContainer = useRef(null);
  const mapInstance = useRef(null); // To store the map instance
  const markersRef = useRef([]); // To store markers for easy management

  // Effect for initializing the map and handling recommendations
  useEffect(() => {
    console.log("KakaoMap useEffect triggered.");
    console.log("Recommendations received:", recommendations);

    const checkKakao = () => {
      console.log("Checking window.kakao:", window.kakao);
      if (window.kakao && window.kakao.maps) {
        console.log("Kakao maps API is loaded.");
        const { kakao } = window;

        // Initialize map if it doesn't exist
        if (!mapInstance.current) {
          console.log("Creating new map instance.");
          const options = {
            center: new kakao.maps.LatLng(33.450701, 126.570667), // Default center (e.g., Jeju Island)
            level: 5,
          };
          mapInstance.current = new kakao.maps.Map(mapContainer.current, options);
        }

        // Clear existing markers
        markersRef.current.forEach(marker => marker.setMap(null));
        markersRef.current = [];

        if (recommendations && recommendations.length > 0) {
          const bounds = new kakao.maps.LatLngBounds();
          let totalLat = 0;
          let totalLon = 0;
          let validLocationsCount = 0;

          recommendations.forEach(location => {
            if (typeof location.latitude === 'number' && typeof location.longitude === 'number') {
              const markerPosition = new kakao.maps.LatLng(location.latitude, location.longitude);

              const marker = new kakao.maps.Marker({
                position: markerPosition,
                map: mapInstance.current,
              });

            const content = `
              <div style="
                padding:10px; 
                background-color:white; 
                border:1px solid #ccc; 
                border-radius:8px; 
                font-size:12px; 
                color:#333; 
                max-width:250px; 
                white-space:normal; 
                word-break:break-all;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
              ">
                <h4 style="margin:0 0 5px 0; font-size:14px; color:#000;">${location.name}</h4>
                ${location.image_url ? `<img src="${location.image_url}" style="width:100%; height:auto; margin-bottom:5px; border-radius:4px;" />` : ''}
                ${location.description ? `<p style="margin:0 0 5px 0;">${location.description}</p>` : ''}
                ${location.activity ? `<p style="margin:0;"><strong>활동:</strong> ${location.activity}</p>` : ''}
              </div>
            `;

            const overlay = new kakao.maps.CustomOverlay({
              content: content,
              map: null,
              position: markerPosition,
              yAnchor: 1.5
            });

            kakao.maps.event.addListener(marker, 'click', function() {
              console.log("Marker clicked! Location:", location);
              // Close any currently open overlay
              if (mapInstance.current.openOverlay) {
                mapInstance.current.openOverlay.setMap(null);
              }
              overlay.setMap(mapInstance.current);
              mapInstance.current.openOverlay = overlay; // Store the currently open overlay
            });

            // Close overlay when map is clicked
            kakao.maps.event.addListener(mapInstance.current, 'click', function() {
              if (mapInstance.current.openOverlay) {
                mapInstance.current.openOverlay.setMap(null);
                mapInstance.current.openOverlay = null;
              }
            });

            markersRef.current.push(marker);
            bounds.extend(markerPosition);

              totalLat += location.latitude;
              totalLon += location.longitude;
              validLocationsCount++;
            }
          });

          // Adjust map bounds to show all markers
          if (recommendations.length > 0) {
            mapInstance.current.setBounds(bounds);
          }

          // If no specific centerLocation is provided, and there are valid locations, center to their average
          if (!centerLocation && validLocationsCount > 0) {
            const avgLat = totalLat / validLocationsCount;
            const avgLon = totalLon / validLocationsCount;
            mapInstance.current.setCenter(new kakao.maps.LatLng(avgLat, avgLon));
          }

        } else {
          console.log("No recommendations to display markers for.");
          // Optionally set a default center if no recommendations
          mapInstance.current.setCenter(new kakao.maps.LatLng(33.450701, 126.570667));
        }

        // Ensure map is properly rendered after container size changes
        mapInstance.current.relayout();

      } else {
        console.log("Kakao maps API not yet loaded, retrying...");
        setTimeout(checkKakao, 100);
      }
    };

    checkKakao();

    // Cleanup function
    return () => {
      if (mapInstance.current) {
        console.log("Cleaning up map instance.");
        markersRef.current.forEach(marker => marker.setMap(null));
        mapInstance.current = null; // Allow re-creation if needed
      }
    };
  }, [recommendations]); // Re-run when recommendations change

  // Effect for handling centerLocation changes
  useEffect(() => {
    if (mapInstance.current && centerLocation) {
      console.log("Centering map to:", centerLocation);
      const { kakao } = window;
      const moveLatLon = new kakao.maps.LatLng(centerLocation.latitude, centerLocation.longitude);
      mapInstance.current.setCenter(moveLatLon);
    }
  }, [centerLocation]); // Re-run when centerLocation changes

  return <div ref={mapContainer} style={{ width: '100%', height: '100%' }} />;
}

export { KakaoMap };