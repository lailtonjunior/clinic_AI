"use client";
import { ButtonHTMLAttributes, forwardRef } from "react";

function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

type Variant = "primary" | "secondary" | "danger" | "outline";

const baseClasses =
  "inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-semibold transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 disabled:opacity-60 disabled:cursor-not-allowed";

const variantClasses: Record<Variant, string> = {
  primary: "bg-sky-600 text-white hover:bg-sky-500 focus-visible:outline-sky-500",
  secondary: "bg-slate-800 text-slate-100 hover:bg-slate-700 focus-visible:outline-slate-600",
  danger: "bg-rose-600 text-white hover:bg-rose-500 focus-visible:outline-rose-500",
  outline:
    "border border-slate-700 text-slate-100 hover:bg-slate-800 focus-visible:outline-slate-600",
};

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
};

export const Button = forwardRef<HTMLButtonElement, Props>(function Button(
  { className, variant = "primary", ...props },
  ref,
) {
  return (
    <button
      ref={ref}
      className={cx(baseClasses, variantClasses[variant], className)}
      {...props}
    />
  );
});
