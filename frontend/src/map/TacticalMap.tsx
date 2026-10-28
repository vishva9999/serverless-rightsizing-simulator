import React, { useEffect, useRef } from 'react';
import L from 'leaflet';

interface TacticalMapProps {
  center?: [number, number];
  zoom?: number;
  className?: string;
}

export const TacticalMap: React.FC<TacticalMapProps> = ({
  center = [37.7749, -122.4194], // Simulated Metro Bay Area
  zoom = 12,
  className = 'h-96 w-full',
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;
    if (mapInstanceRef.current) return; // Prevent double initialization

    // Initialize map
    try {
      const isJsdom = typeof navigator !== 'undefined' && navigator.userAgent.includes('jsdom');
      
      const map = L.map(mapContainerRef.current, {
        center,
        zoom,
        zoomControl: false,
        attributionControl: false,
      });

      // Dark-mode tactical map tiles (CartoDB Dark Matter)
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        subdomains: 'abcd',
      }).addTo(map);

      // In JSDOM test runner, skip SVG vector layers to prevent renderer crashes
      if (!isJsdom) {
        L.control.zoom({ position: 'bottomright' }).addTo(map);

        const hazardCircle = L.circle([37.785, -122.44], {
          color: '#ef4444',
          fillColor: '#dc2626',
          fillOpacity: 0.25,
          radius: 2800,
          weight: 2,
          dashArray: '6, 6',
        }).addTo(map);

        hazardCircle.bindPopup(`
          <div style="font-family: monospace; color: #0f172a; font-size: 12px; padding: 2px;">
            <strong style="color: #dc2626;">[SIMULATED HAZARD]</strong><br/>
            <strong>Type:</strong> Structural Firestorm Cluster<br/>
            <strong>Severity:</strong> Level 4 (Expanding)<br/>
            <strong>Radius:</strong> 2.8 km (Simulated)<br/>
            <strong>Order:</strong> Mandatory Evacuation
          </div>
        `);

        const shelterMarker = L.circleMarker([37.75, -122.40], {
          radius: 9,
          color: '#10b981',
          fillColor: '#059669',
          fillOpacity: 0.85,
          weight: 2,
        }).addTo(map);

        shelterMarker.bindPopup(`
          <div style="font-family: monospace; color: #0f172a; font-size: 12px; padding: 2px;">
            <strong style="color: #059669;">[SIMULATED SHELTER ALPHA]</strong><br/>
            <strong>Capacity:</strong> 650 / 800 Occupied (81%)<br/>
            <strong>Status:</strong> Active Intake<br/>
            <strong>Medical Unit:</strong> Operational
          </div>
        `);

        const shelterBeta = L.circleMarker([37.79, -122.39], {
          radius: 9,
          color: '#06b6d4',
          fillColor: '#0891b2',
          fillOpacity: 0.85,
          weight: 2,
        }).addTo(map);

        shelterBeta.bindPopup(`
          <div style="font-family: monospace; color: #0f172a; font-size: 12px; padding: 2px;">
            <strong style="color: #0891b2;">[SIMULATED SHELTER BETA]</strong><br/>
            <strong>Capacity:</strong> 310 / 1000 Occupied (31%)<br/>
            <strong>Status:</strong> Recommended Destination<br/>
            <strong>Medical Unit:</strong> Operational
          </div>
        `);
      }

      mapInstanceRef.current = map;
    } catch (e) {
      console.warn('Map initialization deferred or headless:', e);
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [center, zoom]);

  return (
    <div className="relative rounded-lg overflow-hidden border border-slate-800 bg-[#0c121e]">
      <div className="absolute top-3 left-3 z-[1000] bg-[#090e17]/90 backdrop-blur-md px-3 py-1.5 rounded border border-slate-700/80 font-mono text-[11px] text-cyan-300 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
        <span>GIS TACTICAL OVERLAY (SYNTHETIC)</span>
      </div>

      <div ref={mapContainerRef} className={className} />
    </div>
  );
};
