"use client";
import { HTMLAttributes } from "react";

function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

type Variant = "default" | "success" | "warning" | "danger";

const variantClasses: Record<Variant, string> = {
  default: "bg-slate-800 text-slate-100",
  success: "bg-emerald-700 text-emerald-50",
  warning: "bg-amber-600 text-amber-50",
  danger: "bg-rose-700 text-rose-50",
};

type Props = HTMLAttributes<HTMLSpanElement> & {
  variant?: Variant;
};

export function Badge({ className, variant = "default", ...props }: Props) {
  return (
    <span
      className={cx(
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold",
        variantClasses[variant],
        className,
      )}
      {...props}
    />
  );
}
