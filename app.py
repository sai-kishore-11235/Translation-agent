import os
import argparse
import pandas as pd
from datetime import datetime
from typing import TypedDict, Annotated, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

def merge_dicts(left: dict, right: dict) -> dict:
    if left is None: left = {}
    if right is None: right = {}
    return {**left, **right}

class TranslationState(TypedDict):
    original_text: str
    translations: Annotated[dict, merge_dicts]
    current_language: str

TARGET_LANGUAGES = {
    "en-US": "English (US)",
    "en-AU": "English (Australia)",
    "vi": "Vietnamese",
    "th": "Thai",
    "hi": "Hindi",
}

def build_app():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GOOGLE_API_KEY")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0.3)

    def translate_text(state: TranslationState) -> TranslationState:
        current_lang = state["current_language"]
        lang_name = TARGET_LANGUAGES[current_lang]
        original_text = state["original_text"]
        prompt = f"""Translate the following text to {lang_name}.
Return only the translation, no explanations or additional text.

Original text: {original_text}

Translation ({lang_name}):"""
        response = llm.invoke([HumanMessage(content=prompt)])
        translation = response.content.strip()
        return {"translations": {current_lang: translation}}

    def create_translation_node(language_code: str):
        def node_func(state: TranslationState) -> TranslationState:
            updated_state = state.copy()
            updated_state["current_language"] = language_code
            return translate_text(updated_state)
        return node_func

    workflow = StateGraph(TranslationState)
    for lang_code in TARGET_LANGUAGES.keys():
        workflow.add_node(lang_code, create_translation_node(lang_code))
    workflow.set_entry_point("en-US")
    workflow.add_edge("en-US", "en-AU")
    workflow.add_edge("en-AU", "vi")
    workflow.add_edge("vi", "th")
    workflow.add_edge("th", "hi")
    workflow.add_edge("hi", END)
    return workflow.compile()

def translate_texts(texts, app):
    rows_out = []
    out_columns = ["Original Text"] + [TARGET_LANGUAGES[lc] for lc in TARGET_LANGUAGES]
    for original_text in texts:
        original_text = "" if pd.isna(original_text) else str(original_text)
        if original_text.strip() == "":
            out_row = {col: "" for col in out_columns}
            out_row["Original Text"] = original_text
        else:
            initial_state = {"original_text": original_text, "translations": {}, "current_language": "en-US"}
            try:
                result = app.invoke(initial_state)
                out_row = {col: "" for col in out_columns}
                out_row["Original Text"] = original_text
                for lc, ln in TARGET_LANGUAGES.items():
                    out_row[ln] = result["translations"].get(lc, "")
            except Exception as e:
                out_row = {col: "" for col in out_columns}
                out_row["Original Text"] = original_text
                first_lang_name = TARGET_LANGUAGES[next(iter(TARGET_LANGUAGES.keys()))]
                out_row[first_lang_name] = f"ERROR: {e}"
        rows_out.append(out_row)
    return pd.DataFrame(rows_out, columns=out_columns)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="./input.xlsx")
    p.add_argument("--text-col", default="Original Text")
    p.add_argument("--output", default=None)
    p.add_argument("--batch-size", type=int, default=10)  # reserved for future streaming/progress use
    args = p.parse_args()

    df_in = pd.read_excel(args.input)
    if args.text_col not in df_in.columns:
        raise ValueError(f"Column '{args.text_col}' not found. Available: {list(df_in.columns)}")

    app = build_app()
    df_out = translate_texts(df_in[args.text_col].tolist(), app)

    out_path = args.output or f"translations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df_out.to_excel(out_path, index=False, sheet_name="Translations")
    print(f"✓ Wrote {len(df_out)} rows to {out_path}")

if __name__ == "__main__":
    main()