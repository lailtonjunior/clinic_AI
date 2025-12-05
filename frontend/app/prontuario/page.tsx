"use client";
import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";

export default function ProntuarioPage() {
  const editor = useEditor({
    extensions: [StarterKit],
    content: "<p>Evolução multiprofissional</p>",
  });

  return (
    <main>
      <h1 className="text-2xl mb-4">Prontuário eletrônico</h1>
      <div className="card">
        <div className="flex gap-2 mb-3">
          <button
            className="px-3 py-1 rounded bg-sky-500 text-sm"
            onClick={() => editor?.chain().focus().toggleBold().run()}
          >
            Negrito
          </button>
          <button
            className="px-3 py-1 rounded bg-sky-500 text-sm"
            onClick={() => editor?.chain().focus().toggleBulletList().run()}
          >
            Lista
          </button>
        </div>
        <div className="rounded bg-slate-900 border border-slate-700 min-h-[200px] p-3">
          <EditorContent editor={editor} />
        </div>
      </div>
    </main>
  );
}
