import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional

df_consultations = pd.read_csv("consultations.csv")
df_tomorrow_predictions = pd.read_csv("predictions_tomorrow.csv")
df_predictions = pd.read_csv("cls_pred_tomorrow_xgb.csv")

st.set_page_config(page_title="상담 분석 대시보드", layout="wide")
st.header("상담 분석 (회귀/분류) — 내일 예측")

def _ensure_ts(df: Optional[pd.DataFrame], col="ts_slot"):
    if df is None or col not in df.columns:
        return df
    if not np.issubdtype(df[col].dtype, np.datetime64):
        df[col] = pd.to_datetime(df[col], errors="coerce")
    if getattr(df[col].dt, "tz", None) is not None:
        df[col] = df[col].dt.tz_convert(None)
    return df

# -----------------------------
# 1) 데이터 로드
# -----------------------------
if df_consultations is None:
    cons_df = pd.DataFrame()
elif isinstance(df_consultations, pd.DataFrame):
    cons_df = df_consultations.copy()
else:
    cons_df = pd.DataFrame(df_consultations)

for c in ["start_time", "end_time", "consultation_date", "ts_slot"]:
    if c in cons_df.columns:
        cons_df[c] = pd.to_datetime(cons_df[c], errors="coerce")
        if getattr(cons_df[c].dt, "tz", None) is not None:
            cons_df[c] = cons_df[c].dt.tz_convert(None)

reg_pred = _ensure_ts(df_tomorrow_predictions, "ts_slot")
cls_pred = _ensure_ts(df_predictions, "ts_slot")

# 전날 실제 상담수 집계
y_actual = None
if "start_time" in cons_df.columns:
    tmp = cons_df.copy()
    tmp["ts_slot"] = pd.to_datetime(tmp["start_time"], errors="coerce").dt.floor("h")
    if getattr(tmp["ts_slot"].dt, "tz", None) is not None:
        tmp["ts_slot"] = tmp["ts_slot"].dt.tz_convert(None)
    y_actual = tmp.groupby("ts_slot").size().rename("y_actual").reset_index()

# -----------------------------
# 2) 표시할 예측일 자동 결정
# -----------------------------
def infer_display_day(*dfs):
    slots = []
    for df in dfs:
        if df is not None and "ts_slot" in df.columns and not df.empty:
            slots.append(pd.to_datetime(df["ts_slot"]).dt.normalize().min())
    return min(slots) if slots else pd.Timestamp.now().normalize()

display_day = infer_display_day(reg_pred, cls_pred)
day_start = display_day
day_end = display_day + pd.Timedelta(days=1)

# -----------------------------
# 3) 전날 실제 합/평균
# -----------------------------
def prev_day_actual_sum_avg(day_df: pd.DataFrame, y_actual_df: Optional[pd.DataFrame]):
    if day_df is None or day_df.empty or y_actual_df is None or y_actual_df.empty:
        return 0.0, 0.0
    pm = day_df[["ts_slot"]].copy()
    pm["ts_prev"] = pm["ts_slot"] - pd.Timedelta(days=1)
    ya = y_actual_df.rename(columns={"ts_slot": "ts_prev"})
    merged = pm.merge(ya, on="ts_prev", how="left")
    merged["y_actual"] = merged["y_actual"].fillna(0)
    return float(merged["y_actual"].sum()), float(merged["y_actual"].mean())

# -----------------------------
# 4) 탭
# -----------------------------
subtab_reg, subtab_cls = st.tabs(["📈 회귀: 다음 날 예측", "🧭 분류: 다음 날 자금유형 Top-3 예측"])

def _badge_by_score(value: float, higher_is_better: bool = True) -> str:
    if value is None:
        return "⚪ 보류"
    v = value if higher_is_better else -value
    if v >= 0.70:
        return "🟢"
    elif v >= 0.50:
        return "🟡"
    return "🔴"

def _reg_badge_rmse(rmse: float) -> str:
    if rmse is None:
        return "⚪"
    if rmse <= 3.0:
        return "🟢"
    elif rmse <= 5.0:
        return "🟡"
    return "🔴"

def render_reg_summary_box():
    st.markdown("#### 🧠 회귀 모델 요약")
    st.caption("최종 Best: **ENS(0.75·XGB_Pois + 0.25·RF)**")
    c1, c2, c3 = st.columns(3)
    c1.metric("RMSE (↓)", "3.668", None, help="실제 상담 건수와 예측 건수의 차이를 시간대별로 평균 제곱근 오차(Root Mean Squared Error)로 측정한 값")
    c2.metric("신뢰 배지", _reg_badge_rmse(3.668), help="RMSE 기준 신뢰도: ≤3.0🟢 (매우 양호) / ≤5.0🟡 (보통) / 그 외🔴")
    c3.caption(
        "• 예측 기준: 과거 상담 로그의 시간대별 상담 건수  \n"
        "• 목표1: **내일 각 시간대별 상담 수** 예측  \n"
        "• 목표2: **내일 각 시간대별 자금유형별 건수** 예측  \n"
        "• 앙상블 가중치: 0.75(XGB_Pois) + 0.25(RF)",
        unsafe_allow_html=True
    )

def render_cls_summary_box():
    st.markdown("#### 🧠 분류 모델 요약")
    auc_macro = 0.8443
    acc = 0.6295
    top3 = 0.9443
    c1, c2, c3 = st.columns(3)
    c1.metric("AUC (macro)", f"{auc_macro:.4f}", _badge_by_score(auc_macro), help="모든 자금유형 클래스 쌍에 대해 구한 ROC-AUC의 Macro 평균 (모델이 클래스 구분을 얼마나 잘하는지)")
    c2.metric("ACC", f"{acc:.4f}", _badge_by_score(acc), help="전체 슬롯 중 올바르게 예측한 비율 (정확도)")
    c3.metric("Top-3 Hit", f"{top3:.4f}", _badge_by_score(top3), help="예측 상위 3개 유형 안에 실제 상담 자금유형이 포함된 비율 (추천 성공률)")
    st.caption(
        "예측 기준: 과거 상담 로그의 시간대·요일·이전 유형 패턴  \n"
        "목표: **내일 각 시간대별 상담의 주요 자금유형(Top-1~3)** 예측  \n"
        "알고리즘: XGBClassifier"
    )

# =============================
# (A) 회귀
# =============================
with subtab_reg:
    st.subheader(f"내일 예측 (회귀) — {day_start:%Y-%m-%d}")
    with st.expander('설명'):
        render_reg_summary_box()

    if reg_pred is None or "ts_slot" not in reg_pred.columns:
        st.info(f"{df_tomorrow_predictions.name} 파일이 없거나 ts_slot 컬럼이 없습니다.")
    else:
        df = reg_pred.copy()
        pred_candidates = ["y_pred", "y_pred_ENS", "y_pred_XGB_Pois", "y_pred_XGB_MSE", "y_pred_RF", "y_pred_HGB_P"]
        pred_col = next((c for c in pred_candidates if c in df.columns), None)
        if pred_col is None:
            st.error(f"예측 컬럼이 없습니다. (가능한 컬럼: {pred_candidates})\n현재 컬럼: {list(df.columns)}")
        else:
            if "y_pred" not in df.columns:
                df["y_pred"] = df[pred_col]

            day_df = (
                df[(df["ts_slot"] >= day_start) & (df["ts_slot"] < day_end)]
                .copy()
                .dropna(subset=["y_pred"])
                .sort_values("ts_slot")
            )

            if day_df.empty:
                st.warning(f"{day_start:%Y-%m-%d} 날짜에 해당하는 예측 슬롯이 없습니다.")
            else:
                total_pred = int(round(day_df["y_pred"].sum()))
                avg_hourly = float(day_df["y_pred"].mean())
                prev_sum, prev_avg = prev_day_actual_sum_avg(day_df, y_actual)
                delta_sum = total_pred - prev_sum
                delta_avg = avg_hourly - prev_avg

                peak_row = day_df.loc[day_df["y_pred"].idxmax()]

                c1, c2, c3 = st.columns(3)
                c1.metric("예측 합계", f"{total_pred:,} 건", f"{delta_sum:+.0f}")
                c2.metric("시간대 평균 예측", f"{avg_hourly:.1f} 건/시간", f"{delta_avg:+.1f}")
                c3.metric("피크 시간대", f"{pd.to_datetime(peak_row['ts_slot']):%m-%d %H시} · {int(round(peak_row['y_pred']))}건")

                st.markdown("---")

                fig_line = px.line(day_df, x="ts_slot", y="y_pred", markers=True, title=f"{day_start:%m-%d} 예측 추이")
                fig_line.update_layout(xaxis_title="시간대", yaxis_title="예측 상담수")
                st.plotly_chart(fig_line, use_container_width=True)

                st.markdown("### 🏆 피크 시간대 Top-5")
                top5 = day_df.sort_values("y_pred", ascending=False).head(5).copy()
                top5["slot_dt"] = pd.to_datetime(top5["ts_slot"])
                top5["slot_str"] = top5["slot_dt"].dt.strftime("%m-%d %H시")
                colz = st.columns(len(top5))
                for i, (_, r) in enumerate(top5.iterrows()):
                    y_now = int(round(r["y_pred"]))
                    delta_text = None
                    if y_actual is not None:
                        prev_ts = r["slot_dt"] - pd.Timedelta(days=1)
                        prev_act = y_actual.loc[y_actual["ts_slot"] == prev_ts, "y_actual"]
                        if len(prev_act):
                            delta_text = f"{y_now - float(prev_act.iloc[0]):+0.0f}"
                    colz[i].metric(f"#{i+1} {r['slot_str']}", f"{y_now} 건", delta_text)

                st.markdown("### 📋 시간대별 예측 상담 수")
                show = day_df[["ts_slot", "y_pred"]].copy().rename(columns={"ts_slot": "시간대", "y_pred": "예측 상담수"})
                st.dataframe(show, use_container_width=True)

# =============================
# (B) 분류
# =============================
with subtab_cls:
    st.subheader(f"내일 자금유형 예측 Top-3 (분류) — {day_start:%Y-%m-%d}")
    with st.expander('설명'):
        render_cls_summary_box()

    if cls_pred is None or "ts_slot" not in cls_pred.columns:
        st.info(f"{df_predictions.name} 파일이 없거나 ts_slot 컬럼이 없습니다.")
    else:
        dc = cls_pred.copy()
        day_dc = dc[(dc["ts_slot"] >= day_start) & (dc["ts_slot"] < day_end)].copy().sort_values("ts_slot")

        if day_dc.empty:
            st.warning(f"{day_start:%Y-%m-%d} 날짜에 해당하는 Top-3 예측 슬롯이 없습니다.")
        else:
            cols = [c for c in ["ts_slot", "pred_label", "top1", "p1", "top2", "p2", "top3", "p3"] if c in day_dc.columns]
            if len(cols) < 2:
                st.info("Top-3 예측 컬럼(top*, p*)이 없습니다.")
            else:
                tbl = day_dc[cols].rename(columns={
                    "ts_slot": "시간대",
                    "pred_label": "Top-1",
                    "top1": "후보1", "p1": "확률1",
                    "top2": "후보2", "p2": "확률2",
                    "top3": "후보3", "p3": "확률3",
                })
                for p in ["확률1", "확률2", "확률3"]:
                    if p in tbl.columns:
                        tbl[p] = tbl[p].astype(float).round(3)
                st.dataframe(tbl, use_container_width=True)

        futc = day_dc.copy()

        top1_col, p1_col = None, None
        if "ens_top1" in futc.columns:
            top1_col = "ens_top1"
            p1_col = "ens_p1" if "ens_p1" in futc.columns else None
        elif "top1" in futc.columns:
            top1_col = "top1"
            p1_col = "p1" if "p1" in futc.columns else None
        elif "pred_label" in futc.columns:
            top1_col = "pred_label"

        if top1_col is None:
            st.info("Top-1 컬럼을 찾을 수 없어 추천 랭킹을 생략합니다.")
        else:
            how = st.radio(
                "집계 기준 선택",
                ["개수 기준(빈도)", "확률합(p1) 기준(모델 확신도)"],
                horizontal=True, index=0, key="rank_mode"
            )

            if how.startswith("개수") or (p1_col is None):
                dist = futc[top1_col].value_counts().reset_index()
                dist.columns = ["fund_type", "score"]
                metric_label = "건"
            else:
                dist = futc.groupby(top1_col)[p1_col].sum().reset_index()
                dist.columns = ["fund_type", "score"]
                metric_label = "점(확률합)"

            top3 = dist.sort_values("score", ascending=False).head(3).reset_index(drop=True)

            st.markdown("### 🏆 예측 추천 Top-3")
            c1, c2, c3 = st.columns(3)
            for i, row in top3.iterrows():
                col = [c1, c2, c3][i]
                col.metric(f"#{i+1} {row['fund_type']}", f"{row['score']:.3f}" if metric_label.startswith("점") else f"{int(row['score'])} {metric_label}")

            fig_pie = px.pie(
                top3, values="score", names="fund_type",
                title="예측 구간 Top-3 비중",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.55
            )
            fig_pie.update_traces(textinfo="label+percent", pull=[0.1, 0.05, 0])
            st.plotly_chart(fig_pie, use_container_width=True)

            with st.expander("전체 랭킹 보기"):
                st.dataframe(dist.sort_values("score", ascending=False).reset_index(drop=True), use_container_width=True)
