"use client";
import { HTMLAttributes, TdHTMLAttributes, ThHTMLAttributes } from "react";

function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

type Props = HTMLAttributes<HTMLTableElement>;

export function Table({ className, ...props }: Props) {
  return (
    <table
      className={cx(
        "w-full border border-slate-800 text-sm text-slate-100 overflow-hidden rounded-lg",
        className,
      )}
      {...props}
    />
  );
}

export function TableHead(props: HTMLAttributes<HTMLTableSectionElement>) {
  return <thead className="bg-slate-900/70 text-slate-400" {...props} />;
}

export function TableBody(props: HTMLAttributes<HTMLTableSectionElement>) {
  return <tbody className="divide-y divide-slate-800" {...props} />;
}

export function TableRow(props: HTMLAttributes<HTMLTableRowElement>) {
  return <tr className="hover:bg-slate-900/40" {...props} />;
}

export function TableHeaderCell(props: ThHTMLAttributes<HTMLTableCellElement>) {
  return <th className="px-3 py-2 text-left font-semibold" {...props} />;
}

export function TableCell(props: TdHTMLAttributes<HTMLTableCellElement>) {
  return <td className="px-3 py-2 align-top" {...props} />;
}
