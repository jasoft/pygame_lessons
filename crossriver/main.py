import streamlit as st
import time


def create_person(x, y, color):
    return f'<circle cx="{x}" cy="{y}" r="10" fill="{color}" stroke="black" stroke-width="1" />'


def create_boat(x, y, width, height):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="brown" />'


def river_crossing_simulation():
    st.set_page_config(layout="wide")
    st.title("河流渡船模拟")

    total_people = 20
    boat_capacity = 4
    return_capacity = 3
    people_left = total_people
    people_crossed = 0
    crossings = 0

    left_col, right_col = st.columns(2)

    with left_col:
        st.header("左岸")
        left_svg = st.empty()
        left_count = st.empty()

    with right_col:
        st.header("右岸")
        right_svg = st.empty()
        right_count = st.empty()

    boat_position = "left"
    boat_passengers = 0

    def update_scene():
        svg_width = 300
        svg_height = 200
        person_radius = 10
        persons_per_row = 10

        left_scene = f'<svg width="{svg_width}" height="{svg_height}">'
        right_scene = f'<svg width="{svg_width}" height="{svg_height}">'

        # 添加河流
        left_scene += (
            f'<rect x="0" y="150" width="{svg_width}" height="50" fill="lightblue" />'
        )
        right_scene += (
            f'<rect x="0" y="150" width="{svg_width}" height="50" fill="lightblue" />'
        )

        # 添加人
        for i in range(people_left):
            row = i // persons_per_row
            col = i % persons_per_row
            x = 20 + col * (person_radius * 2 + 5)
            y = 20 + row * (person_radius * 2 + 5)
            left_scene += create_person(x, y, "blue")

        for i in range(people_crossed):
            row = i // persons_per_row
            col = i % persons_per_row
            x = 20 + col * (person_radius * 2 + 5)
            y = 20 + row * (person_radius * 2 + 5)
            right_scene += create_person(x, y, "blue")

        # 添加船
        if boat_position == "left":
            left_scene += create_boat(200, 140, 80, 20)
            for i in range(boat_passengers):
                color = "green" if i == 0 else "blue"
                left_scene += create_person(220 + i * 20, 135, color)
        else:
            right_scene += create_boat(20, 140, 80, 20)
            for i in range(boat_passengers):
                color = "green" if i == 0 else "blue"
                right_scene += create_person(40 + i * 20, 135, color)

        left_scene += "</svg>"
        right_scene += "</svg>"

        left_svg.markdown(left_scene, unsafe_allow_html=True)
        right_svg.markdown(right_scene, unsafe_allow_html=True)
        left_count.markdown(f"**左岸人数: {people_left}**")
        right_count.markdown(f"**右岸人数: {people_crossed}**")

    status_text = st.empty()

    while people_left > 0 or boat_passengers > 0:
        if boat_position == "left":
            # 装船
            people_to_cross = min(boat_capacity, people_left)
            people_left -= people_to_cross
            boat_passengers = people_to_cross
            status_text.text(f"第 {crossings + 1} 次渡河: {people_to_cross} 人上船")
            update_scene()
            time.sleep(2)

            # 过河
            boat_position = "right"
            status_text.text(f"第 {crossings + 1} 次渡河: 船正在过河")
            update_scene()
            time.sleep(2)

            # 下船
            people_crossed += boat_passengers
            boat_passengers = 0
            crossings += 1
            status_text.text(f"第 {crossings} 次渡河完成: {people_to_cross} 人下船")
            update_scene()
            time.sleep(2)

        else:  # boat_position == "right"
            if people_left > 0:
                # 一个人回去
                boat_passengers = 1
                people_crossed -= 1
                status_text.text(f"第 {crossings + 1} 次渡河: 1 人上船准备回去")
                update_scene()
                time.sleep(2)

                # 过河
                boat_position = "left"
                status_text.text(f"第 {crossings + 1} 次渡河: 船正在回去")
                update_scene()
                time.sleep(2)

                # 到达左岸
                people_left += 1
                boat_passengers = 0
                crossings += 1
                status_text.text(f"第 {crossings} 次渡河完成: 1 人回到左岸")
                update_scene()
                time.sleep(2)
            else:
                break

    st.success(f"所有人已经过河! 总共需要 {crossings} 次渡河。")


if __name__ == "__main__":
    river_crossing_simulation()
