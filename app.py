import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="양자 인지 기반 인간-AI 시스템",
    page_icon="🧠",
    layout="wide"
)

# -----------------------------
# 기본 설정
# -----------------------------
if "result" not in st.session_state:
    st.session_state.result = None

if "previous_result" not in st.session_state:
    st.session_state.previous_result = None

if "feedback" not in st.session_state:
    st.session_state.feedback = None

if "user_choice" not in st.session_state:
    st.session_state.user_choice = None

st.title("🧠 양자 인지 기반 인간-AI 상호작용 시스템")

st.write(
    "사용자의 판단 기준과 선호를 반영하여 "
    "다양한 가능성을 탐색하고 의사결정을 지원합니다."
)

st.divider()

# -----------------------------
# STEP 1. 상황 입력
# -----------------------------
st.header("① 의사결정 상황 입력")

situation = st.text_area(
    "어떤 상황에서 의사결정을 하고 싶으신가요?",
    placeholder="예: 진로 선택, 학습 방법, 일상적인 의사결정 등",
    height=100
)

goal = st.text_input(
    "이번 의사결정에서 원하는 목표는 무엇인가요?",
    placeholder="예: 나의 흥미와 미래 발전 가능성을 고려하고 싶다."
)

# -----------------------------
# STEP 2. 대안 설정
# -----------------------------
st.divider()
st.header("② 다양한 가능성 설정")

st.write("비교하고 싶은 대안을 직접 입력하세요.")

alternatives = []

for i in range(1, 4):
    name = st.text_input(
        f"대안 {i}",
        placeholder=f"비교할 선택지 {i}",
        key=f"alternative_{i}"
    )

    if name.strip():
        alternatives.append(name.strip())

# -----------------------------
# STEP 3. 판단 기준 체크리스트
# -----------------------------
st.divider()
st.header("③ 나의 판단 기준 선택")

st.write(
    "현재 상황에서 중요하게 생각하는 기준을 "
    "직접 선택하세요."
)

criteria = {
    "효율성": "시간과 노력을 효율적으로 활용할 수 있는가?",
    "안정성": "위험과 불확실성을 줄일 수 있는가?",
    "만족도": "개인의 흥미와 만족을 충족하는가?",
    "발전 가능성": "장기적으로 성장할 가능성이 있는가?",
    "경제성": "비용과 자원을 합리적으로 활용할 수 있는가?",
    "실현 가능성": "현재 조건에서 실제로 실행할 수 있는가?"
}

selected = {}

for criterion, description in criteria.items():
    selected[criterion] = st.checkbox(
        f"{criterion} - {description}",
        value=criterion in [
            "효율성", "만족도", "발전 가능성"
        ],
        key=f"check_{criterion}"
    )

active_criteria = [
    c for c in criteria if selected[c]
]

st.write("### 선택한 기준의 중요도")

weights = {}

for criterion in active_criteria:
    weights[criterion] = st.slider(
        f"{criterion}의 중요도",
        min_value=1,
        max_value=5,
        value=3,
        key=f"weight_{criterion}"
    )

# -----------------------------
# STEP 4. 대안별 특성 평가
# -----------------------------
st.divider()
st.header("④ 대안별 특성 평가")

st.write(
    "각 대안이 선택한 판단 기준을 얼마나 충족하는지 "
    "평가하세요. 1점은 낮음, 5점은 높음입니다."
)

ratings = {}

for i, alternative in enumerate(alternatives):

    with st.expander(
        f"📌 {alternative} 평가하기",
        expanded=True
    ):

        ratings[alternative] = {}

        for criterion in active_criteria:

            ratings[alternative][criterion] = st.slider(
                f"{criterion} 충족 정도",
                min_value=1,
                max_value=5,
                value=3,
                key=f"rating_{i}_{criterion}"
            )

# -----------------------------
# STEP 5. 분석 실행
# -----------------------------
st.divider()
st.header("⑤ 사용자 선호 기반 가능성 분석")

if st.button("가능성 분석하기", type="primary"):

    if not situation.strip():
        st.warning("의사결정 상황을 입력하세요.")

    elif not goal.strip():
        st.warning("원하는 목표를 입력하세요.")

    elif len(alternatives) < 2:
        st.warning("비교할 대안을 최소 2개 입력하세요.")

    elif len(set(alternatives)) != len(alternatives):
        st.warning("서로 다른 대안을 입력하세요.")

    elif not active_criteria:
        st.warning("최소 하나 이상의 판단 기준을 선택하세요.")

    else:
        total_weight = sum(weights.values())

        scores = {}

        for alternative in alternatives:

            weighted_score = sum(
                ratings[alternative][criterion]
                * weights[criterion]
                for criterion in active_criteria
            )

            scores[alternative] = (
                weighted_score / total_weight
            )

        ranking = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # 이전 분석 결과 보관
        st.session_state.previous_result = (
            st.session_state.result
        )

        st.session_state.result = {
            "situation": situation,
            "goal": goal,
            "scores": scores,
            "ranking": ranking,
            "weights": weights.copy(),
            "criteria": active_criteria.copy()
        }

        # 새로운 분석 시 이전 피드백 초기화
        st.session_state.feedback = None
        st.session_state.user_choice = None

# -----------------------------
# STEP 6. 분석 결과 표시
# -----------------------------
if st.session_state.result is not None:

    result = st.session_state.result

    st.success("분석이 완료되었습니다.")

    st.subheader("대안별 종합 평가")

    chart_data = pd.DataFrame({
        "평가 점수": result["scores"]
    })

    st.bar_chart(chart_data)

    for name, score in result["ranking"]:
        st.write(f"**{name}** : {score:.2f} / 5점")

    recommended = result["ranking"][0][0]

    st.info(
        f"현재 설정한 판단 기준에서 "
        f"'{recommended}'이(가) 가장 높은 평가를 받았습니다."
    )

    st.subheader("추천 판단 근거")

    for criterion in result["criteria"]:
        st.write(
            f"- {criterion}: 중요도 "
            f"{result['weights'][criterion]}/5, "
            f"추천 대안의 충족도 "
            f"{ratings[recommended][criterion]}/5"
        )

    st.caption(
        "※ 평가 점수는 사용자 선호를 반영한 가중 평균입니다. "
        "실제 확률이나 양자컴퓨터의 계산 결과가 아닙니다."
    )

    # -------------------------
    # 이전 분석과 비교
    # -------------------------
    previous = st.session_state.previous_result

    if previous is not None:

        st.divider()
        st.subheader("이전 분석과 결과 비교")

        comparison = pd.DataFrame({
            "이전 분석": previous["scores"],
            "현재 분석": result["scores"]
        }).fillna(0)

        st.bar_chart(comparison)

        old_best = previous["ranking"][0][0]
        new_best = result["ranking"][0][0]

        if old_best != new_best:
            st.success(
                f"판단 기준을 수정한 후 추천 대안이 "
                f"'{old_best}'에서 '{new_best}'으로 바뀌었습니다."
            )
        else:
            st.info(
                "판단 기준을 수정했지만 추천 대안은 유지되었습니다."
            )

    # -------------------------
    # STEP 7. 사용자 선택
    # -------------------------
    st.divider()
    st.header("⑥ 인간의 최종 판단")

    user_choice = st.radio(
        "AI 분석을 참고하여 어떤 대안을 선택하시겠습니까?",
        list(result["scores"].keys()),
        key="choice_widget"
    )

    feedback = st.selectbox(
        "AI 분석 결과에 대한 생각을 선택하세요.",
        [
            "AI 분석에 동의한다.",
            "AI 추천과 다른 선택을 하고 싶다.",
            "추가적인 정보를 고려하고 싶다.",
            "판단 기준의 중요도를 수정하고 싶다."
        ],
        key="feedback_widget"
    )

    if st.button("사용자 피드백 제출"):

        st.session_state.user_choice = user_choice
        st.session_state.feedback = feedback

        st.rerun()

    # -------------------------
    # STEP 8. 피드백 반영
    # -------------------------
    if st.session_state.feedback is not None:

        st.divider()
        st.subheader("⑦ 사용자 피드백 및 재분석")

        st.write(
            f"AI 추천: **{recommended}**"
        )

        st.write(
            f"사용자 선택: **{st.session_state.user_choice}**"
        )

        st.write(
            f"사용자 의견: {st.session_state.feedback}"
        )

        if st.session_state.user_choice == recommended:

            st.success(
                "AI 분석과 사용자의 선택이 일치합니다."
            )

        else:

            st.info(
                "사용자는 AI의 추천과 다른 선택을 했습니다. "
                "사용자의 판단을 존중하며 추가적인 선호를 반영할 수 있습니다."
            )

        st.markdown("### 판단 기준 수정하기")

        st.write(
            "위쪽의 체크리스트에서 기준을 추가하거나 제외하고, "
            "중요도를 다시 설정해 보세요."
        )

        st.write(
            "수정한 조건으로 '가능성 분석하기'를 다시 누르면 "
            "이전 결과와 새로운 결과를 비교할 수 있습니다."
        )

        st.caption(
            "사용자 피드백을 바탕으로 판단 기준을 직접 수정하는 "
            "반복적 의사결정 과정입니다."
        )

st.divider()

st.caption(
    "본 프로그램은 양자 인지론의 맥락 의존적 판단과 "
    "양자 컴퓨팅의 복수 가능성 처리 방식에서 착안한 "
    "인간-AI 상호작용 모의 인터페이스입니다."
)
