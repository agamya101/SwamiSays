import React from 'react';

interface ProgressRingProps {
  radius?: number;
  stroke?: number;
  progress: number; // 0 to 1
  className?: string;
}

export const ProgressRing: React.FC<ProgressRingProps> = ({
  radius = 42,
  stroke = 4,
  progress,
  className = ''
}) => {
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - Math.min(1, Math.max(0, progress)) * circumference;

  return (
    <svg
      height={radius * 2}
      width={radius * 2}
      className={`progress-ring ${className}`}
      aria-hidden="true"
    >
      <circle
        stroke="var(--line)"
        fill="transparent"
        strokeWidth={stroke}
        r={normalizedRadius}
        cx={radius}
        cy={radius}
      />
      <circle
        stroke="var(--accent)"
        fill="transparent"
        strokeWidth={stroke}
        strokeDasharray={`${circumference} ${circumference}`}
        style={{ strokeDashoffset }}
        strokeLinecap="round"
        r={normalizedRadius}
        cx={radius}
        cy={radius}
        className="progress-ring-circle"
      />
    </svg>
  );
};
