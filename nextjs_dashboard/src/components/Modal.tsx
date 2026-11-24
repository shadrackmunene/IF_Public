"use client";

import { useEffect, type ReactNode } from "react";

/** Pop-up window in the self-assessment style: title row with a top-right ×, a Close button at the bottom,
 *  closes on Escape or a click on the dimmed background. The page behind does not scroll while it is open. */
export default function Modal({ title, onClose, children, wide = false }: {
  title: ReactNode; onClose: () => void; children: ReactNode; wide?: boolean;
}) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [onClose]);

  return (
    <div className="modal-backdrop" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className={"modal" + (wide ? " wide" : "")} role="dialog" aria-modal="true" aria-label={typeof title === "string" ? title : undefined}>
        <div className="modal-head"><h3>{title}</h3><button className="modal-x" aria-label="Close" onClick={onClose}>×</button></div>
        <div className="modal-body">{children}</div>
        <div className="modal-foot"><button className="btn" onClick={onClose}>Close</button></div>
      </div>
    </div>
  );
}
