import React from 'react';

interface ChipProps {
  label: string;
  onClick?: () => void;
  active?: boolean;
  className?: string;
  role?: string;
}

export const Chip: React.FC<ChipProps> = ({
  label,
  onClick,
  active = false,
  className = '',
  role
}) => {
  return (
    <button
      type="button"
      role={role}
      onClick={onClick}
      className={`chip ${active ? 'active' : ''} ${className}`}
    >
      {label}
    </button>
  );
};
