import React from 'react';

interface MandalaWatermarkProps {
  size?: number;
  className?: string;
  animate?: boolean;
}

export const MandalaWatermark: React.FC<MandalaWatermarkProps> = ({
  size = 360,
  className = '',
  animate = true
}) => {
  return (
    <div
      className={`mandala-watermark-wrap ${className}`}
      style={{ width: size, height: size }}
      aria-hidden="true"
    >
      <svg
        viewBox="0 0 300 300"
        width={size}
        height={size}
        fill="none"
        stroke="var(--accent)"
        strokeWidth="1.2"
        className={animate ? 'mandala-float' : ''}
      >
        <circle cx="150" cy="150" r="140" strokeDasharray="3 3" />
        <circle cx="150" cy="150" r="110" />
        <circle cx="150" cy="150" r="70" />
        <circle cx="150" cy="150" r="28" strokeDasharray="2 2" />

        {/* 8 radiating lotus petals */}
        {[0, 45, 90, 135, 180, 225, 270, 315].map((angle) => (
          <g key={angle} transform={`rotate(${angle} 150 150)`}>
            <path
              d="M150 150 C120 90 120 40 150 20 C180 40 180 90 150 150 Z"
              fill="none"
            />
            <path
              d="M150 150 C135 110 135 75 150 50 C165 75 165 110 150 150 Z"
              strokeDasharray="2 2"
            />
            <circle cx="150" cy="30" r="3" fill="var(--accent)" />
          </g>
        ))}
      </svg>
    </div>
  );
};
