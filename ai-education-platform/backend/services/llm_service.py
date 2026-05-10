import json
import random
from datetime import datetime

class LLMService:

    async def analyze_text(self, text: str, analysis_type: str) -> dict:
        if analysis_type == "performance":
            return {
                "summary": f"基于对{text}的分析，该学生在以下方面表现突出：基础概念理解扎实，课堂参与度较高。但在应用型题目和综合分析方面仍有提升空间。",
                "strengths": [
                    "基础概念掌握牢固，定义和定理记忆准确",
                    "课堂出勤率高，学习态度认真",
                    "作业完成及时，书写规范"
                ],
                "weaknesses": [
                    "综合应用能力有待加强",
                    "解决复杂问题时思路不够清晰",
                    "对新题型的适应能力需要提升"
                ],
                "score_trend": "稳中有升，最近三次测验分数分别为72、78、85",
                "recommendation": "建议增加综合练习题的训练量，特别是跨知识点的综合应用题。每周安排2-3次专项练习。"
            }
        elif analysis_type == "learning_style":
            return {
                "learning_style": "视觉型+实践型",
                "description": "该学生倾向于通过图表、思维导图等视觉化方式理解概念，同时在动手实践中学习效果最佳。",
                "preferences": [
                    "喜欢看教学视频和图解",
                    "通过编程实践理解算法效果好",
                    "小组讨论中参与度高"
                ],
                "suggestions": [
                    "推荐使用思维导图整理知识点",
                    "多使用在线编程练习平台",
                    "建议观看配套教学视频辅助理解"
                ]
            }
        else:
            return {
                "analysis": f"对{text}的深度分析结果",
                "confidence": 0.87,
                "details": "分析完成，详见各项指标"
            }

    async def generate_questions(self, topic: str, difficulty: str, count: int = 5) -> dict:
        questions_db = {
            "极限计算": {
                "基础": [
                    {"question": "求极限 lim(x→1) (x²-1)/(x-1)", "answer": "2", "hint": "因式分解后约分"},
                    {"question": "求极限 lim(x→0) sin(3x)/x", "answer": "3", "hint": "利用重要极限 lim(x→0) sin(x)/x = 1"},
                    {"question": "求极限 lim(x→∞) (2x+1)/(x-3)", "answer": "2", "hint": "分子分母同除以最高次项x"},
                ],
                "中等": [
                    {"question": "求极限 lim(x→0) (1-cos(x))/x²", "answer": "1/2", "hint": "利用等价无穷小或洛必达法则"},
                    {"question": "求极限 lim(x→0) (e^x - 1)/x", "answer": "1", "hint": "利用e^x的泰勒展开或洛必达法则"},
                ],
                "困难": [
                    {"question": "求极限 lim(x→0) (sin(x) - x)/x³", "answer": "-1/6", "hint": "使用泰勒展开 sin(x) = x - x³/6 + ..."},
                    {"question": "证明 lim(n→∞) (1+1/n)^n = e", "answer": "利用单调有界定理或夹逼定理", "hint": "先证单调性，再证有界性"},
                ]
            },
            "链表操作": {
                "基础": [
                    {"question": "描述单链表和双链表的主要区别", "answer": "单链表每个节点只有后继指针，双链表有前驱和后继两个指针", "hint": "从节点结构角度分析"},
                    {"question": "在单链表头部插入一个节点的时间复杂度是？", "answer": "O(1)", "hint": "只需修改头指针"},
                ],
                "中等": [
                    {"question": "编写判断单链表是否有环的算法思路", "answer": "快慢指针法：快指针每次走两步，慢指针每次走一步，若相遇则有环", "hint": "Floyd判圈算法"},
                    {"question": "如何O(1)时间删除单链表中给定节点（非尾节点）？", "answer": "将后继节点的值复制到当前节点，然后删除后继节点", "hint": "值覆盖法"},
                ],
                "困难": [
                    {"question": "如何检测两个单链表的交叉点？", "answer": "先求两链表长度差d，让长链表先走d步，然后同时走直到相遇", "hint": "双指针法，考虑长度差"},
                ]
            },
            "Python编程": {
                "基础": [
                    {"question": "Python中列表(list)和元组(tuple)的区别是什么？", "answer": "列表可变，元组不可变；列表用[]，元组用()", "hint": "从可变性角度分析"},
                    {"question": "Python中的装饰器是什么？请举例说明", "answer": "装饰器是一个接受函数作为参数并返回新函数的高阶函数，用@语法糖调用", "hint": "闭包的应用"},
                ],
                "中等": [
                    {"question": "解释Python中的GIL及其影响", "answer": "GIL是全局解释器锁，确保同一时刻只有一个线程执行Python字节码，限制了CPU密集型任务的多线程性能", "hint": "Global Interpreter Lock"},
                ],
                "困难": [
                    {"question": "实现一个Python上下文管理器来管理数据库连接", "answer": "实现__enter__和__exit__方法，或使用contextmanager装饰器", "hint": "with语句的底层机制"},
                ]
            }
        }

        topic_questions = questions_db.get(topic, questions_db.get("极限计算", {}))
        difficulty_questions = topic_questions.get(difficulty, topic_questions.get("基础", []))
        selected = difficulty_questions[:min(count, len(difficulty_questions))]

        return {
            "topic": topic,
            "difficulty": difficulty,
            "questions": selected,
            "total_count": len(selected),
            "estimated_time": len(selected) * 8,
            "tips": f"建议在{len(selected) * 8}分钟内完成，每题仔细审题后再作答。"
        }

    async def generate_explanation(self, topic: str, question: str) -> dict:
        explanations = {
            "极限计算": {
                "explanation": """

极限是微积分的基础概念，描述函数在某一点附近的行为趋势。

1. **直接代入法**：若函数在该点连续，直接代入即可
2. **因式分解法**：适用于0/0型，通过分解约去零因子
3. **洛必达法则**：对0/0或∞/∞型，对分子分母分别求导
4. **等价无穷小替换**：sin(x)~x, tan(x)~x, e^x-1~x, ln(1+x)~x (x→0)
5. **泰勒展开**：将函数展开为幂级数

- 使用洛必达法则前必须验证是否为0/0或∞/∞型
- 等价无穷小只能在乘除中替换，加减中不能直接替换
- 注意区分左极限和右极限""",
                "key_formulas": [
                    "lim(x→0) sin(x)/x = 1",
                    "lim(x→∞) (1+1/x)^x = e",
                    "lim(x→0) (e^x-1)/x = 1"
                ]
            },
            "链表操作": {
                "explanation": """

链表是一种动态数据结构，通过指针将节点串联起来，无需连续内存空间。

1. **插入操作**：修改指针指向，注意处理头节点特殊情况
2. **删除操作**：找到前驱节点，修改其next指针
3. **查找操作**：从头节点顺序遍历
4. **反转操作**：三指针法（prev, curr, next）

| 操作 | 单链表 | 双链表 |
|------|--------|--------|
| 头部插入 | O(1) | O(1) |
| 尾部插入 | O(n) | O(1) |
| 查找 | O(n) | O(n) |
| 删除给定节点 | O(n) | O(1) |""",
                "key_formulas": []
            }
        }

        return explanations.get(topic, {
            "explanation": "暂无相关知识点解析",
            "key_formulas": []
        })

    async def generate_study_plan(self, student_info: dict) -> dict:
        name = student_info.get("name", "同学")
        weak_points = student_info.get("weak_points", [])
        course = student_info.get("course", "课程")

        weak_text = "、".join(weak_points) if weak_points else "各知识点"

        return {
            "student_name": name,
            "course": course,
            "plan_duration": "4周",
            "weekly_plan": [
                {
                    "week": 1,
                    "theme": "基础巩固",
                    "tasks": [
                        f"复习{weak_points[0] if weak_points else '基础概念'}的核心定义和定理",
                        "完成基础练习题20道",
                        "观看相关教学视频2-3个",
                        "整理错题集"
                    ],
                    "daily_time": "1.5小时",
                    "goal": "夯实基础，建立知识框架"
                },
                {
                    "week": 2,
                    "theme": "重点突破",
                    "tasks": [
                        f"针对{weak_text}进行专项训练",
                        "完成中等难度练习题15道",
                        "参加线上讨论答疑",
                        "总结解题方法和技巧"
                    ],
                    "daily_time": "2小时",
                    "goal": "突破重点难点，提升解题能力"
                },
                {
                    "week": 3,
                    "theme": "综合提升",
                    "tasks": [
                        "完成综合应用题10道",
                        "进行模拟测试",
                        "查漏补缺，复习错题",
                        "与同学进行学习交流"
                    ],
                    "daily_time": "2小时",
                    "goal": "提升综合应用能力"
                },
                {
                    "week": 4,
                    "theme": "冲刺复习",
                    "tasks": [
                        "完成历年真题练习",
                        "全面复习知识点",
                        "调整心态，保持良好作息",
                        "进行最后的查漏补缺"
                    ],
                    "daily_time": "1.5小时",
                    "goal": "全面复习，自信应考"
                }
            ],
            "resources": [
                {"type": "视频", "title": f"{course}重点难点讲解", "url": "/resources/video"},
                {"type": "练习", "title": f"{weak_text}专项训练", "url": "/resources/exercise"},
                {"type": "文档", "title": "知识点总结手册", "url": "/resources/summary"}
            ],
            "tips": [
                "每天固定时间段学习，养成良好习惯",
                "学习45分钟休息10分钟，保持注意力",
                "遇到问题及时请教老师或同学",
                "坚持做笔记，记录学习心得"
            ]
        }

    async def generate_teaching_suggestions(self, class_data: dict) -> dict:
        course_name = class_data.get("course_name", "课程")
        avg_score = class_data.get("avg_score", 75)
        weak_topics = class_data.get("weak_topics", [])

        return {
            "course": course_name,
            "overall_assessment": f"当前班级整体{course_name}成绩处于{'良好' if avg_score >= 80 else '中等' if avg_score >= 60 else '需加强'}水平，平均分{avg_score}分。",
            "common_issues": [
                {"issue": f"{weak_topics[0] if weak_topics else '基础概念'}理解不深入", "severity": "高",
                 "affected_ratio": "45%",
                 "detail": "约45%的学生在该知识点的测试中得分率低于60%"},
                {"issue": "解题步骤不规范", "severity": "中",
                 "affected_ratio": "30%",
                 "detail": "部分学生解题过程跳步，缺少必要的推导步骤"},
                {"issue": "综合应用能力不足", "severity": "中",
                 "affected_ratio": "35%",
                 "detail": "面对跨知识点的综合题，学生普遍表现不佳"}
            ],
            "teaching_adjustments": [
                {
                    "area": "教学内容",
                    "suggestion": f"增加{weak_topics[0] if weak_topics else '重点知识点'}的讲解时间和练习量",
                    "priority": "高",
                    "expected_impact": "预计可提升该知识点平均分10-15分"
                },
                {
                    "area": "教学方法",
                    "suggestion": "引入更多实际案例和可视化教学工具",
                    "priority": "中",
                    "expected_impact": "提升学生学习兴趣和理解深度"
                },
                {
                    "area": "课堂互动",
                    "suggestion": "增加课堂提问和小组讨论环节",
                    "priority": "中",
                    "expected_impact": "提高课堂参与度，及时发现学生困惑"
                }
            ],
            "recommended_activities": [
                {"type": "课堂练习", "description": f"针对{weak_topics[0] if weak_topics else '薄弱环节'}设计专项课堂练习"},
                {"type": "分组讨论", "description": "将学生按水平分组，进行互助学习"},
                {"type": "个别辅导", "description": "对成绩下滑明显的学生进行一对一辅导"}
            ],
            "student_groups": {
                "excellent": {"count": 8, "action": "提供拓展学习资源，培养创新能力"},
                "good": {"count": 15, "action": "巩固基础，适度提升"},
                "need_help": {"count": 5, "action": "重点辅导，建立帮扶机制"}
            }
        }

    async def analyze_exam(self, exam_data: dict) -> dict:
        return {
            "exam_title": exam_data.get("title", "考试"),
            "overall_analysis": {
                "avg_score": 76.5,
                "highest_score": 95,
                "lowest_score": 42,
                "pass_rate": "82%",
                "excellent_rate": "25%",
                "standard_deviation": 12.3,
                "difficulty_coefficient": 0.765,
                "discrimination": 0.42
            },
            "question_analysis": [
                {
                    "question_num": 1,
                    "topic": "基础概念",
                    "correct_rate": "85%",
                    "analysis": "大部分学生掌握良好，少数学生对基本定义理解有偏差"
                },
                {
                    "question_num": 2,
                    "topic": "计算题",
                    "correct_rate": "62%",
                    "analysis": "计算错误率较高，部分学生运算能力需要加强"
                },
                {
                    "question_num": 3,
                    "topic": "证明题",
                    "correct_rate": "45%",
                    "analysis": "证明题得分率最低，学生逻辑推理能力普遍薄弱"
                },
                {
                    "question_num": 4,
                    "topic": "应用题",
                    "correct_rate": "58%",
                    "analysis": "审题能力不足，部分学生未能正确建立数学模型"
                }
            ],
            "improvement_strategies": [
                {
                    "target": "计算能力",
                    "strategy": "每天安排10分钟速算练习，培养运算准确性",
                    "priority": "高"
                },
                {
                    "target": "证明推理",
                    "strategy": "系统讲解常见证明方法，提供阶梯式证明练习",
                    "priority": "高"
                },
                {
                    "target": "审题能力",
                    "strategy": "加强应用题训练，教授审题技巧和建模方法",
                    "priority": "中"
                }
            ],
            "grade_distribution": {
                "90-100": 5,
                "80-89": 10,
                "70-79": 8,
                "60-69": 6,
                "below_60": 3
            }
        }

llm_service = LLMService()