import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Lesson } from '../types';
import { getDone, totalDone } from '../lib/progress';
import { PetalSheet } from './PetalSheet';
import { ProgressRing } from './ProgressRing';

interface IkigaiWheelProps {
  lessons: Lesson[];
}

export const IkigaiWheel: React.FC<IkigaiWheelProps> = ({ lessons }) => {
  const [selectedLesson, setSelectedLesson] = useState<Lesson | null>(null);
  const [hoveredCircleIdx, setHoveredCircleIdx] = useState<number | null>(null);
  const [closestTextIdx, setClosestTextIdx] = useState<number | null>(null);

  const svgRef = useRef<SVGSVGElement | null>(null);
  const circleRefs = useRef<(SVGCircleElement | null)[]>([]);
  const pointerPosRef = useRef<{ clientX: number; clientY: number } | null>(null);

  const completedTotal = totalDone();
  const overallRatio = Math.min(1, completedTotal / 48);

  const updateHoverState = useCallback(() => {
    const svg = svgRef.current;
    const pt = pointerPosRef.current;
    if (!svg || !pt) {
      setHoveredCircleIdx(null);
      setClosestTextIdx(null);
      return;
    }

    const svgRect = svg.getBoundingClientRect();
    // Pointer coordinate transformed to SVG 400x400 space
    const px = ((pt.clientX - svgRect.left) / svgRect.width) * 400;
    const py = ((pt.clientY - svgRect.top) / svgRect.height) * 400;

    // Ignore center circle (hub radius ~46 at 200, 200)
    const distFromCenter = Math.hypot(px - 200, py - 200);
    if (distFromCenter < 48) {
      setHoveredCircleIdx(null);
      setClosestTextIdx(null);
      return;
    }

    let minCircleDist = Infinity;
    let closestCircleIdx: number | null = null;
    let circleCenterInSvg = { x: 200, y: 200 };

    for (let i = 0; i < lessons.length; i++) {
      const circleEl = circleRefs.current[i];
      if (!circleEl) continue;
      const cRect = circleEl.getBoundingClientRect();
      const cx = ((cRect.left + cRect.width / 2 - svgRect.left) / svgRect.width) * 400;
      const cy = ((cRect.top + cRect.height / 2 - svgRect.top) / svgRect.height) * 400;
      const d = Math.hypot(px - cx, py - cy);

      // Select circle based on distance from pointer to circle center (radius 78)
      if (d <= 78 && d < minCircleDist) {
        minCircleDist = d;
        closestCircleIdx = i;
        circleCenterInSvg = { x: cx, y: cy };
      }
    }

    if (closestCircleIdx === null) {
      setHoveredCircleIdx(null);
      setClosestTextIdx(null);
      return;
    }

    setHoveredCircleIdx(closestCircleIdx);

    // Identify the static outer text label to which this rotating circle is currently closest
    let minTextDist = Infinity;
    let bestTextIdx = 0;
    for (let t = 0; t < lessons.length; t++) {
      const tAngleDeg = t * 45 - 90;
      const tAngleRad = (tAngleDeg * Math.PI) / 180;
      const lx = 200 + 138 * Math.cos(tAngleRad);
      const ly = 200 + 138 * Math.sin(tAngleRad);
      const td = Math.hypot(circleCenterInSvg.x - lx, circleCenterInSvg.y - ly);
      if (td < minTextDist) {
        minTextDist = td;
        bestTextIdx = t;
      }
    }

    setClosestTextIdx(bestTextIdx);
  }, [lessons.length]);

  // Keep hover dynamically synchronized while outer circles rotate
  useEffect(() => {
    let animId: number;
    const tick = () => {
      if (pointerPosRef.current) {
        updateHoverState();
      }
      animId = requestAnimationFrame(tick);
    };
    animId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animId);
  }, [updateHoverState]);

  const handlePointerMove = (e: React.PointerEvent<SVGSVGElement>) => {
    pointerPosRef.current = { clientX: e.clientX, clientY: e.clientY };
    updateHoverState();
  };

  const handlePointerLeave = () => {
    pointerPosRef.current = null;
    setHoveredCircleIdx(null);
    setClosestTextIdx(null);
  };

  const handleClick = () => {
    if (closestTextIdx !== null && lessons[closestTextIdx]) {
      setSelectedLesson(lessons[closestTextIdx]);
    }
  };

  return (
    <div className="wheel-container">
      <div className="wheel-svg-wrap">
        <svg
          ref={svgRef}
          viewBox="0 0 400 400"
          className="wheel-svg"
          aria-label="The 8-petal Swami Chakra"
          role="region"
          onPointerMove={handlePointerMove}
          onPointerLeave={handlePointerLeave}
          onClick={handleClick}
          style={{ cursor: hoveredCircleIdx !== null ? 'pointer' : 'default' }}
        >
          {/* Rotating petals group */}
          <g
            className="wheel-petal-group animate-spin"
            style={{
              transformBox: 'view-box',
              transformOrigin: '200px 200px'
            }}
          >
            {lessons.map((lesson, idx) => {
              const angleDeg = idx * 45 - 90;
              const angleRad = (angleDeg * Math.PI) / 180;
              const cx = 200 + 85 * Math.cos(angleRad);
              const cy = 200 + 85 * Math.sin(angleRad);
              const doneCount = getDone(lesson.id).length;
              const opacity = 0.12 + 0.10 * (doneCount / 6);
              const isHovered = hoveredCircleIdx === idx;

              return (
                <circle
                  key={`petal-${lesson.id}`}
                  ref={(el) => (circleRefs.current[idx] = el)}
                  cx={cx}
                  cy={cy}
                  r="78"
                  fill="var(--accent)"
                  fillOpacity={opacity}
                  stroke="var(--accent)"
                  strokeWidth={isHovered ? '4' : '1.5'}
                  strokeOpacity={isHovered ? 1 : 0.45}
                  style={{
                    mixBlendMode: 'multiply',
                    transition: 'stroke-width 0.15s ease, stroke-opacity 0.15s ease'
                  }}
                  className={`wheel-petal ${isHovered ? 'wheel-petal-hovered' : ''}`}
                />
              );
            })}
          </g>

          {/* Upright text labels around outer perimeter - pointer events disabled to remove text hover */}
          <g>
            {lessons.map((lesson, idx) => {
              const angleDeg = idx * 45 - 90;
              const angleRad = (angleDeg * Math.PI) / 180;
              const lx = 200 + 138 * Math.cos(angleRad);
              const ly = 200 + 138 * Math.sin(angleRad);
              const isTextHighlighted = closestTextIdx === idx;

              return (
                <text
                  key={`label-${lesson.id}`}
                  x={lx}
                  y={ly}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className="wheel-petal-text"
                  style={{
                    fontSize: isTextHighlighted ? '14px' : '13px',
                    fill: isTextHighlighted ? 'var(--accent)' : 'var(--ink)',
                    fontWeight: isTextHighlighted ? 800 : 700,
                    pointerEvents: 'none',
                    userSelect: 'none',
                    transition: 'fill 0.15s ease, font-size 0.15s ease'
                  }}
                >
                  <tspan
                    x={lx}
                    dy="-5"
                    style={{
                      fontSize: '11px',
                      fill: isTextHighlighted ? 'var(--accent)' : 'var(--muted)'
                    }}
                  >
                    #{lesson.id}
                  </tspan>
                  <tspan x={lx} dy="14">
                    {lesson.title}
                  </tspan>
                </text>
              );
            })}
          </g>

          {/* Center Circle: YOU + overall progress (farther center circle - ignored from petal hover) */}
          <g transform="translate(200, 200)" style={{ pointerEvents: 'none' }}>
            <circle
              r="46"
              fill="var(--surface)"
              stroke="var(--line)"
              strokeWidth="2"
            />
            {/* Embedded progress ring inside center */}
            <g transform="translate(-46, -46)">
              <ProgressRing
                radius={46}
                stroke={4}
                progress={overallRatio}
              />
            </g>
            <text
              y="-3"
              textAnchor="middle"
              dominantBaseline="middle"
              style={{
                fontFamily: 'var(--font-head)',
                fontSize: '15px',
                fontWeight: 700,
                fill: 'var(--ink)'
              }}
            >
              YOU
            </text>
            <text
              y="16"
              textAnchor="middle"
              dominantBaseline="middle"
              style={{
                fontSize: '11px',
                fontWeight: 600,
                fill: 'var(--muted)'
              }}
            >
              {completedTotal}/48
            </text>
          </g>
        </svg>
      </div>

      <PetalSheet
        lesson={selectedLesson}
        onClose={() => setSelectedLesson(null)}
      />
    </div>
  );
};
