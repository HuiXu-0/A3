# 系统架构文档

## 1. 整体架构

本系统采用前后端分离的 B/S 架构，后端基于 Python FastAPI 框架，前端使用 Vue 3 构建单页应用。

### 核心设计原则
- **模块化**：各功能模块独立，低耦合高内聚
- **可扩展**：LLM 服务可插拔，支持从 Mock 切换到真实大模型
- **角色隔离**：基于 RBAC 的权限控制，四种角色数据隔离
- **异步优先**：全链路 async/await，高并发友好

## 2. 多智能体系统设计

### 2.1 Agent 架构图

```
                    ┌──────────────────────┐
                    │   LLM 服务层 (可插拔)  │
                    │  Mock / API / 本地模型  │
                    └──────────┬───────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
    ┌───────┴───────┐  ┌──────┴──────┐  ┌───────┴───────┐
    │ 学情分析Agent  │  │ 资源生成Agent│  │ 教学优化Agent  │
    │               │  │             │  │               │
    │ • 成绩趋势    │  │ • 练习题生成 │  │ • 教学建议    │
    │ • 薄弱点识别  │  │ • 知识解析   │  │ • 进度调整    │
    │ • 学习风格    │  │ • 学习计划   │  │ • 重点推荐    │
    │ • 风险预警    │  │ • 视频推荐   │  │ • 班级画像    │
    └───────────────┘  └─────────────┘  └───────────────┘
            │                  │                  │
            └──────────────────┼──────────────────┘
                               │
                    ┌──────────┴───────────┐
                    │    考试分析Agent      │
                    │ • 题目难度分析       │
                    │ • 失分模式识别       │
                    │ • 改进策略生成       │
                    └──────────────────────┘
```

### 2.2 Agent 协作流程

1. **数据采集阶段**：从数据库获取学生的成绩、出勤、作业、学习记录
2. **分析阶段**：学情分析Agent 识别薄弱点和学习风格
3. **资源生成阶段**：资源生成Agent 基于分析结果生成个性化内容
4. **教学反馈阶段**：教学优化Agent 向教师提供教学调整建议
5. **考试复盘阶段**：考试分析Agent 深度分析考试数据，反馈到其他Agent

### 2.3 LLM 服务层

采用**策略模式**，支持三种实现：
- `MockLLMService`：开发/演示用，返回预设的高质量模拟响应
- `APILLMService`：对接 OpenAI / 百度文心 / 讯飞星火等云端API
- `LocalLLMService`：对接本地部署的大模型（如 ChatGLM、LLaMA）

## 3. 数据库设计

### 3.1 核心表结构

#### users - 用户表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| username | TEXT UNIQUE | 登录账号 |
| name | TEXT | 姓名 |
| password_hash | TEXT | 密码哈希 |
| role | TEXT | 角色(student/teacher/counselor/admin) |
| class_name | TEXT | 班级 |
| major | TEXT | 专业 |
| created_at | TEXT | 创建时间 |

#### courses - 课程表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| name | TEXT | 课程名称 |
| teacher_id | INTEGER FK | 授课教师 |
| class_name | TEXT | 授课班级 |
| schedule | TEXT | 上课时间 |
| description | TEXT | 课程描述 |

#### assignments - 作业表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| course_id | INTEGER FK | 所属课程 |
| title | TEXT | 作业标题 |
| content | TEXT | 作业内容 |
| deadline | TEXT | 截止时间 |

#### submissions - 作业提交表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| assignment_id | INTEGER FK | 作业ID |
| student_id | INTEGER FK | 学生ID |
| content | TEXT | 提交内容 |
| score | REAL | 得分 |
| feedback | TEXT | 批改反馈 |
| submit_time | TEXT | 提交时间 |
| graded | INTEGER | 是否已批改 |

#### exams - 考试表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| course_id | INTEGER FK | 所属课程 |
| title | TEXT | 考试名称 |
| total_score | REAL | 总分 |
| exam_time | TEXT | 考试时间 |

#### exam_results - 考试成绩表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| exam_id | INTEGER FK | 考试ID |
| student_id | INTEGER FK | 学生ID |
| score | REAL | 得分 |
| weak_points | TEXT(JSON) | 薄弱知识点 |

#### attendance - 签到表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| course_id | INTEGER FK | 课程ID |
| student_id | INTEGER FK | 学生ID |
| date | TEXT | 签到日期 |
| status | TEXT | 状态(present/absent/late) |
| check_in_time | TEXT | 签到时间 |

#### leave_requests - 请假申请表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| student_id | INTEGER FK | 学生ID |
| type | TEXT | 类型(leave/outing) |
| reason | TEXT | 请假理由 |
| status | TEXT | 状态(pending/approved/rejected) |
| approver_id | INTEGER FK | 审批人ID |

#### learning_profiles - 学习画像表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| student_id | INTEGER FK | 学生ID |
| course_id | INTEGER FK | 课程ID |
| weak_points | TEXT(JSON) | 薄弱知识点列表 |
| strong_points | TEXT(JSON) | 擅长知识点列表 |
| learning_style | TEXT | 学习风格 |

#### resources - 学习资源表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| title | TEXT | 资源标题 |
| type | TEXT | 类型(video/article/practice) |
| url | TEXT | 资源链接 |
| course_id | INTEGER FK | 关联课程 |
| tags | TEXT(JSON) | 标签 |
| difficulty | INTEGER | 难度等级(1-5) |

#### chat_messages - 聊天消息表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| sender_id | INTEGER FK | 发送者ID |
| receiver_id | INTEGER FK | 接收者ID(私聊) |
| group_id | INTEGER FK | 群组ID(群聊) |
| content | TEXT | 消息内容 |
| msg_type | TEXT | 消息类型 |
| created_at | TEXT | 发送时间 |

#### announcements - 公告表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| class_name | TEXT | 班级 |
| content | TEXT | 公告内容 |
| author_id | INTEGER FK | 发布者ID |

#### ai_analysis - AI分析记录表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| student_id | INTEGER FK | 学生ID |
| course_id | INTEGER FK | 课程ID |
| analysis_type | TEXT | 分析类型 |
| content | TEXT(JSON) | 分析结果 |
| created_at | TEXT | 分析时间 |

### 3.2 ER 关系图

```
users ──┬── courses (teacher_id)
        ├── submissions (student_id)
        ├── attendance (student_id)
        ├── leave_requests (student_id)
        ├── exam_results (student_id)
        ├── learning_profiles (student_id)
        ├── chat_messages (sender_id, receiver_id)
        └── announcements (author_id)

courses ──┬── courseware (course_id)
          ├── assignments (course_id)
          ├── exams (course_id)
          ├── resources (course_id)
          └── attendance (course_id)

assignments ──── submissions (assignment_id)
exams ──── exam_results (exam_id)
```

## 4. API 端点列表

### 4.1 认证模块 `/api/auth`
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /login | 用户登录 |
| POST | /register | 用户注册 |
| GET | /me | 获取当前用户信息 |

### 4.2 学生模块 `/api/student`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /courses | 获取学生课程列表 |
| GET | /assignments/{course_id} | 获取课程作业 |
| POST | /submit-assignment | 提交作业 |
| GET | /exams/{course_id} | 获取考试列表 |
| GET | /exam-results/{student_id} | 获取考试成绩 |
| GET | /resources/{course_id} | 获取个性化资源 |
| POST | /leave-request | 提交请假申请 |
| GET | /schedule | 获取课表 |
| GET | /learning-profile/{student_id}/{course_id} | 获取学习画像 |
| GET | /dorm-bills | 获取宿舍账单 |
| GET | /study-records | 获取学习记录 |

### 4.3 教师模块 `/api/teacher`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /courses | 获取教师课程 |
| POST | /upload-courseware | 上传课件 |
| POST | /create-assignment | 创建作业 |
| GET | /submissions/{assignment_id} | 获取提交列表 |
| POST | /grade-submission | 批改作业 |
| GET | /attendance/{course_id} | 获取签到记录 |
| POST | /take-attendance | 发起签到 |
| GET | /class-analysis/{course_id} | 班级分析 |
| POST | /create-exam | 创建考试 |
| GET | /exam-analysis/{exam_id} | 考试分析 |

### 4.4 辅导员模块 `/api/counselor`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /leave-requests | 获取请假列表 |
| POST | /approve-leave/{id} | 审批请假 |
| GET | /student-grades/{class_name} | 班级成绩 |
| GET | /student-alerts/{class_name} | 学业预警 |
| GET | /class-overview/{class_name} | 班级总览 |

### 4.5 管理员模块 `/api/admin`
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /server-status | 服务器状态 |
| GET | /bug-reports | Bug报告 |
| GET | /system-stats | 系统统计 |
| GET | /all-users | 用户列表 |
| POST | /manage-user | 管理用户 |

### 4.6 聊天模块 `/api/chat`
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /send-message | 发送消息 |
| GET | /messages/{user_id} | 获取消息 |
| GET | /groups | 获取群组 |
| POST | /create-group | 创建群组 |
| GET | /group-messages/{group_id} | 获取群消息 |

### 4.7 智能体模块 `/api/agents`
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /analyze-student | 学情分析 |
| POST | /generate-resources | 资源生成 |
| POST | /exam-analysis-ai | 考试分析 |
| POST | /learning-plan | 学习计划生成 |
| POST | /teaching-suggestions | 教学建议 |

## 5. 安全设计

### 5.1 认证机制
- JWT Token 认证，登录后签发，请求时通过 `Authorization: Bearer <token>` 传递
- Token 有效期 24 小时，过期需重新登录
- 密码使用 bcrypt 哈希存储

### 5.2 权限控制 (RBAC)
- 四种角色：student、teacher、counselor、admin
- API 路由级别权限校验
- 前端菜单根据角色动态生成
- 数据访问隔离：学生只能访问自己的数据

### 5.3 数据安全
- SQL 注入防护：使用参数化查询
- XSS 防护：前端输出转义
- CORS 配置：生产环境限制来源

## 6. 前端组件架构

```
App
├── Login (登录页)
├── Layout (主布局)
│   ├── Sidebar (侧边栏 - 角色自适应)
│   ├── Header (顶栏 - 用户信息/通知)
│   └── Content (内容区 - 路由视图)
│       ├── StudentDashboard
│       ├── StudentCourses → CourseDetail
│       ├── StudentAssignments
│       ├── StudentExams
│       ├── StudentResources
│       ├── StudentChat
│       ├── StudentLeave
│       ├── StudentSchedule
│       ├── StudentReminders
│       ├── TeacherDashboard
│       ├── TeacherCourses → TeacherCourseDetail
│       ├── TeacherAttendance
│       ├── TeacherGrading
│       ├── TeacherExamAnalysis
│       ├── TeacherAssignments
│       ├── CounselorDashboard
│       ├── CounselorLeaveManagement
│       ├── CounselorStudentGrades
│       ├── CounselorClassOverview
│       ├── AdminDashboard
│       ├── AdminUsers
│       ├── AdminSystem
│       └── AIAnalysisCenter
```
