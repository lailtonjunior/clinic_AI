"use client";
import { forwardRef, InputHTMLAttributes, ReactNode } from "react";

function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

type Props = InputHTMLAttributes<HTMLInputElement> & {
  label?: ReactNode;
  error?: string;
};

export const Input = forwardRef<HTMLInputElement, Props>(function Input(
  { label, error, className, ...props },
  ref,
) {
  return (
    <label className="block space-y-1">
      {label && <span className="text-sm text-slate-200">{label}</span>}
      <input
        ref={ref}
        className={cx(
          "w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500",
          className,
        )}
        {...props}
      />
      {error && <span className="text-xs text-rose-400">{error}</span>}
    </label>
  );
});
