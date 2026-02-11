"""
차트 컴포넌트 - Plotly 기반 시각화
도넛 차트, 타임라인, 스파크라인
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any, Optional
from datetime import datetime, date


def render_donut_chart(
    labels: List[str],
    values: List[float],
    colors: Optional[List[str]] = None,
    title: str = "",
    center_text: Optional[str] = None,
    height: int = 300,
) -> None:
    """도넛 차트 렌더링
    
    Args:
        labels: 라벨 리스트
        values: 값 리스트
        colors: 색상 리스트
        title: 차트 제목
        center_text: 중앙 텍스트
        height: 차트 높이
    """
    if not labels or not values:
        st.caption("데이터가 없습니다.")
        return
    
    # 기본 색상
    if not colors:
        colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker=dict(colors=colors),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=13),
    )])
    
    # 중앙 텍스트 추가
    if center_text:
        fig.add_annotation(
            text=center_text,
            x=0.5,
            y=0.5,
            font=dict(size=24, color='#1a1d21', family='Pretendard'),
            showarrow=False,
        )
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(size=16, color='#1a1d21'),
        ),
        margin=dict(t=60, b=40, l=40, r=40),
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5,
        ),
    )
    
    st.plotly_chart(fig, use_container_width=True, key=f"donut_{title}")


def render_timeline_chart(
    data: List[Dict[str, Any]],
    title: str = "현장 타임라인",
    height: int = 400,
) -> None:
    """타임라인 차트 렌더링 (Gantt 스타일)
    
    Args:
        data: [{"name": "현장명", "start": date, "end": date, "status": "상태"}, ...]
        title: 차트 제목
        height: 차트 높이
    """
    if not data:
        st.caption("데이터가 없습니다.")
        return
    
    # 상태별 색상
    status_colors = {
        "건축허가": "#9ca3af",
        "착공예정": "#3b82f6",
        "착공중": "#f59e0b",
        "준공": "#10b981",
    }
    
    # Plotly 타임라인 데이터 준비
    timeline_data = []
    for item in data:
        timeline_data.append(dict(
            Task=item.get("name", ""),
            Start=item.get("start"),
            Finish=item.get("end"),
            Resource=item.get("status", ""),
        ))
    
    # 색상 매핑
    colors = {status: status_colors.get(status, "#6b7280") for status in set(d["Resource"] for d in timeline_data)}
    
    fig = px.timeline(
        timeline_data,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Resource",
        color_discrete_map=colors,
        title=title,
    )
    
    fig.update_layout(
        height=height,
        margin=dict(t=60, b=40, l=200, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=13, color='#495057'),
        xaxis=dict(
            title="기간",
            gridcolor='#f1f3f5',
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=12),
        ),
        showlegend=True,
        legend=dict(
            title="현장상태",
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
        ),
    )
    
    st.plotly_chart(fig, use_container_width=True, key=f"timeline_{title}")


def render_bar_chart(
    labels: List[str],
    values: List[float],
    title: str = "",
    orientation: str = "v",
    color: str = "#3b82f6",
    height: int = 300,
) -> None:
    """막대 차트 렌더링
    
    Args:
        labels: 라벨 리스트
        values: 값 리스트
        title: 차트 제목
        orientation: 방향 ("v" 또는 "h")
        color: 막대 색상
        height: 차트 높이
    """
    if not labels or not values:
        st.caption("데이터가 없습니다.")
        return
    
    if orientation == "h":
        fig = go.Figure(data=[go.Bar(
            x=values,
            y=labels,
            orientation='h',
            marker_color=color,
            text=values,
            textposition='outside',
            textfont=dict(size=13, color='#1a1d21'),
        )])
        
        fig.update_layout(
            xaxis=dict(title="건수", gridcolor='#f1f3f5'),
            yaxis=dict(tickfont=dict(size=13)),
        )
    else:
        fig = go.Figure(data=[go.Bar(
            x=labels,
            y=values,
            marker_color=color,
            text=values,
            textposition='outside',
            textfont=dict(size=13, color='#1a1d21'),
        )])
        
        fig.update_layout(
            xaxis=dict(tickfont=dict(size=13)),
            yaxis=dict(title="건수", gridcolor='#f1f3f5'),
        )
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(size=16),
        ),
        margin=dict(t=60, b=40, l=100, r=40),
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=13, color='#495057'),
    )
    
    st.plotly_chart(fig, use_container_width=True, key=f"bar_{title}")


def render_line_chart(
    x_data: List[Any],
    y_data: List[float],
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    color: str = "#3b82f6",
    fill: bool = True,
    height: int = 300,
) -> None:
    """라인 차트 렌더링
    
    Args:
        x_data: X축 데이터
        y_data: Y축 데이터
        title: 차트 제목
        x_label: X축 라벨
        y_label: Y축 라벨
        color: 라인 색상
        fill: 영역 채우기 여부
        height: 차트 높이
    """
    if not x_data or not y_data:
        st.caption("데이터가 없습니다.")
        return
    
    fig = go.Figure()
    
    if fill:
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines',
            line=dict(color=color, width=3),
            fill='tozeroy',
            fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)',
        ))
    else:
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines+markers',
            line=dict(color=color, width=3),
            marker=dict(size=8, color=color),
        ))
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(size=16),
        ),
        margin=dict(t=60, b=40, l=60, r=40),
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=13, color='#495057'),
        xaxis=dict(
            title=x_label,
            gridcolor='#f1f3f5',
        ),
        yaxis=dict(
            title=y_label,
            gridcolor='#f1f3f5',
        ),
    )
    
    st.plotly_chart(fig, use_container_width=True, key=f"line_{title}")


def render_sparkline(
    data: List[float],
    color: str = "#3b82f6",
    height: int = 50,
) -> str:
    """스파크라인 HTML 생성
    
    Args:
        data: 데이터 리스트
        color: 라인 색상
        height: 차트 높이
        
    Returns:
        HTML 문자열
    """
    if not data or len(data) < 2:
        return ""
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=data,
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2)',
    ))
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
    )
    
    return fig.to_html(include_plotlyjs=False, config={'displayModeBar': False})
