

const { createApp, ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } = Vue;
const { createRouter, createWebHashHistory } = VueRouter;



const StudentDashboard = {
  template: `<div class="dashboard">
    <div class="stats-grid">
      <div class="stat-card" v-for="s in stats" :key="s.label">
        <div class="stat-icon" :style="{background: s.bg}"><i :class="s.icon"></i></div>
        <div class="stat-info"><div class="stat-value">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
      </div>
    </div>
    <div class="grid-2">
      <div class="card">
        <div class="card-header"><h3>今日课程</h3></div>
        <div class="card-body">
          <div v-if="todayCourses.length === 0" class="empty-state">今天没有课程安排</div>
          <div v-for="c in todayCourses" :key="c.id" class="list-item">
            <div class="list-item-icon"><i class="fas fa-book"></i></div>
            <div class="list-item-info">
              <div class="list-item-title">{{ c.name }}</div>
              <div class="list-item-desc">{{ c.schedule }} | {{ c.teacher_name }}</div>
            </div>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-header"><h3>待完成作业</h3></div>
        <div class="card-body">
          <div v-if="pendingAssignments.length === 0" class="empty-state">暂无待完成作业</div>
          <div v-for="a in pendingAssignments" :key="a.id" class="list-item">
            <div class="list-item-icon" style="color:var(--warning)"><i class="fas fa-file-alt"></i></div>
            <div class="list-item-info">
              <div class="list-item-title">{{ a.title }}</div>
              <div class="list-item-desc">截止: {{ a.deadline }}</div>
            </div>
            <span class="badge badge-warning">待提交</span>
          </div>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-header"><h3>AI学习建议</h3></div>
      <div class="card-body">
        <div class="ai-suggestion">
          <div class="ai-icon"><i class="fas fa-robot"></i></div>
          <div class="ai-content">
            <p>根据您最近的学习情况分析：</p>
            <ul>
              <li>高等数学成绩呈上升趋势，继续保持</li>
              <li>数据结构的链表部分需要加强练习</li>
              <li>建议每天投入30分钟复习算法基础</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>`,
  setup() {
    const stats = ref([
      { label: '已修学分', value: '24', icon: 'fas fa-star', bg: 'var(--primary-bg)' },
      { label: '待交作业', value: '3', icon: 'fas fa-file-alt', bg: 'var(--warning-bg)' },
      { label: '平均分', value: '82.5', icon: 'fas fa-chart-line', bg: 'var(--success-bg)' },
      { label: '学习时长', value: '126h', icon: 'fas fa-clock', bg: 'var(--danger-bg)' }
    ]);
    const todayCourses = ref([]);
    const pendingAssignments = ref([]);
    onMounted(async () => {
      try {
        const courses = await api.student.getCourses();
        todayCourses.value = (courses || []).slice(0, 3);
      } catch(e) { console.error(e); }
      try {
        const hw = await api.student.getAssignments(1);
        pendingAssignments.value = (hw || []).filter(a => !a.graded).slice(0, 3);
      } catch(e) {}
    });
    return { stats, todayCourses, pendingAssignments };
  }
};

const StudentCourses = {
  template: `<div>
    <div class="card">
      <div class="card-header"><h3>我的课程</h3></div>
      <div class="card-body">
        <div v-if="courses.length === 0" class="empty-state">暂无课程</div>
        <div class="grid-3">
          <div v-for="c in courses" :key="c.id" class="course-card" @click="$router.push('/student/course/' + c.id)">
            <div class="course-card-header" :style="{background: colors[c.id % colors.length]}">
              <i class="fas fa-book-open"></i>
            </div>
            <div class="course-card-body">
              <h4>{{ c.name }}</h4>
              <p><i class="fas fa-user"></i> {{ c.teacher_name || '教师' }}</p>
              <p><i class="fas fa-clock"></i> {{ c.schedule }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>`,
  setup() {
    const courses = ref([]);
    const colors = ['#4A90D9','#52C41A','#FAAD14','#FF4D4F','#722ED1'];
    onMounted(async () => { try { courses.value = await api.student.getCourses() || []; } catch(e) {} });
    return { courses, colors };
  }
};

const StudentCourseDetail = {
  template: `<div>
    <div class="card">
      <div class="card-header"><h3>{{ course.name || '课程详情' }}</h3>
        <div class="tabs">
          <button v-for="t in tabs" :key="t.key" :class="['tab', activeTab===t.key?'active':'']" @click="activeTab=t.key">
            <i :class="t.icon"></i> {{ t.label }}
          </button>
        </div>
      </div>
      <div class="card-body">
        <div v-if="activeTab==='courseware'">
          <div v-if="courseware.length===0" class="empty-state">暂无课件</div>
          <div v-for="c in courseware" :key="c.id" class="list-item">
            <div class="list-item-icon"><i class="fas fa-file-pdf" style="color:var(--danger)"></i></div>
            <div class="list-item-info"><div class="list-item-title">{{ c.title }}</div><div class="list-item-desc">{{ c.upload_time }}</div></div>
            <button class="btn btn-sm btn-outline">下载</button>
          </div>
        </div>
        <div v-if="activeTab==='assignments'">
          <div v-if="assignments.length===0" class="empty-state">暂无作业</div>
          <div v-for="a in assignments" :key="a.id" class="list-item">
            <div class="list-item-icon"><i class="fas fa-file-alt" style="color:var(--warning)"></i></div>
            <div class="list-item-info"><div class="list-item-title">{{ a.title }}</div><div class="list-item-desc">截止: {{ a.deadline }}</div></div>
            <span :class="['badge', a.graded ? 'badge-success' : 'badge-warning']">{{ a.graded ? '已批改' : '待提交' }}</span>
          </div>
        </div>
        <div v-if="activeTab==='resources'">
          <div v-if="resources.length===0" class="empty-state">暂无推荐资源</div>
          <div class="grid-3">
            <div v-for="r in resources" :key="r.id" class="resource-card">
              <div class="resource-type"><i :class="r.icon"></i></div>
              <h4>{{ r.title }}</h4>
              <p>{{ r.desc }}</p>
              <div class="resource-meta"><span class="badge">{{ r.difficulty }}</span></div>
            </div>
          </div>
        </div>
        <div v-if="activeTab==='profile'">
          <div v-if="!profile" class="empty-state">暂无学习画像数据</div>
          <div v-else class="profile-content">
            <div class="profile-section"><h4>薄弱知识点</h4><div class="tags"><span v-for="w in profile.weak_points" :key="w" class="tag tag-danger">{{ w }}</span></div></div>
            <div class="profile-section"><h4>擅长知识点</h4><div class="tags"><span v-for="s in profile.strong_points" :key="s" class="tag tag-success">{{ s }}</span></div></div>
            <div class="profile-section"><h4>学习风格</h4><p>{{ profile.learning_style }}</p></div>
          </div>
        </div>
      </div>
    </div>
  </div>`,
  setup() {
    const route = VueRouter.useRoute();
    const activeTab = ref('courseware');
    const course = ref({});
    const courseware = ref([]);
    const assignments = ref([]);
    const resources = ref([]);
    const profile = ref(null);
    const tabs = [
      { key: 'courseware', label: '课件', icon: 'fas fa-file-powerpoint' },
      { key: 'assignments', label: '作业', icon: 'fas fa-tasks' },
      { key: 'resources', label: '资源', icon: 'fas fa-lightbulb' },
      { key: 'profile', label: '学习画像', icon: 'fas fa-chart-pie' }
    ];
    onMounted(async () => {
      const id = route.params.id;
      try {
        const courses = await api.student.getCourses();
        course.value = (courses || []).find(c => c.id == id) || {};
      } catch(e) {}
      try { assignments.value = await api.student.getAssignments(id) || []; } catch(e) {}
      try {
        const p = await api.request(`/student/learning-profile/1/${id}`);
        if (p && p.weak_points) profile.value = p;
      } catch(e) {}
    });
    return { activeTab, course, courseware, assignments, resources, profile, tabs };
  }
};

const StudentAssignments = {
  template: `<div class="card"><div class="card-header"><h3>我的作业</h3></div><div class="card-body">
    <div v-if="assignments.length===0" class="empty-state">暂无作业</div>
    <div class="table-wrapper"><table class="table"><thead><tr><th>课程</th><th>作业</th><th>截止时间</th><th>状态</th><th>分数</th></tr></thead>
    <tbody><tr v-for="a in assignments" :key="a.id"><td>{{ a.course_name }}</td><td>{{ a.title }}</td><td>{{ a.deadline }}</td>
    <td><span :class="['badge', a.graded?'badge-success':'badge-warning']">{{ a.graded?'已批改':'待提交' }}</span></td>
    <td>{{ a.score ?? '-' }}</td></tr></tbody></table></div>
  </div></div>`,
  setup() {
    const assignments = ref([]);
    onMounted(async () => { try { assignments.value = await api.student.getAssignments(1) || []; } catch(e) {} });
    return { assignments };
  }
};

const StudentExams = {
  template: `<div class="card"><div class="card-header"><h3>考试成绩</h3></div><div class="card-body">
    <div v-if="results.length===0" class="empty-state">暂无考试记录</div>
    <div v-for="r in results" :key="r.id" class="exam-card">
      <div class="exam-header"><h4>{{ r.exam_title }}</h4><span class="exam-score">{{ r.score }}分</span></div>
      <div class="exam-bar"><div class="exam-bar-fill" :style="{width: (r.score/r.total_score*100)+'%', background: r.score>=60?'var(--success)':'var(--danger)'}"></div></div>
      <div v-if="r.weak_points && r.weak_points.length" class="exam-weak"><strong>薄弱点：</strong><span v-for="w in r.weak_points" :key="w" class="tag tag-danger" style="margin:2px">{{ w }}</span></div>
    </div>
  </div></div>`,
  setup() {
    const results = ref([]);
    onMounted(async () => { try { results.value = await api.student.getExamResults(1) || []; } catch(e) {} });
    return { results };
  }
};

const StudentResources = {
  template: `<div class="card"><div class="card-header"><h3>个性化学习资源</h3>
    <button class="btn btn-primary btn-sm" @click="generateResources"><i class="fas fa-magic"></i> AI生成资源</button></div>
    <div class="card-body">
    <div v-if="loading" class="loading"><i class="fas fa-spinner fa-spin"></i> AI正在分析您的学情并生成个性化资源...</div>
    <div v-else-if="resources.length===0" class="empty-state">点击上方按钮获取AI推荐资源</div>
    <div v-else class="grid-3">
      <div v-for="r in resources" :key="r.title" class="resource-card">
        <div class="resource-type"><i :class="r.type==='video'?'fas fa-play-circle':r.type==='practice'?'fas fa-pen':'fas fa-book'"></i></div>
        <h4>{{ r.title }}</h4><p>{{ r.description }}</p>
        <div class="resource-meta"><span class="badge" :class="'badge-'+r.level">{{ r.difficulty }}</span></div>
      </div>
    </div>
  </div></div>`,
  setup() {
    const resources = ref([]);
    const loading = ref(false);
    const generateResources = async () => {
      loading.value = true;
      try {
        const res = await api.agents.generateResources({ student_id: 1, course_id: 1 });
        resources.value = res?.resources || [];
      } catch(e) { console.error(e); }
      loading.value = false;
    };
    return { resources, loading, generateResources };
  }
};

const StudentChat = {
  template: `<div class="chat-container">
    <div class="chat-sidebar">
      <div class="chat-sidebar-header"><h4>消息</h4></div>
      <div v-for="c in contacts" :key="c.id" :class="['chat-contact', selectedContact?.id===c.id?'active':'']" @click="selectContact(c)">
        <div class="contact-avatar">{{ c.name[0] }}</div>
        <div class="contact-info"><div class="contact-name">{{ c.name }}</div><div class="contact-role">{{ roleMap[c.role] }}</div></div>
      </div>
    </div>
    <div class="chat-main">
      <div v-if="!selectedContact" class="empty-state">选择联系人开始聊天</div>
      <template v-else>
        <div class="chat-header"><h4>{{ selectedContact.name }}</h4></div>
        <div class="chat-messages" ref="msgContainer">
          <div v-for="m in messages" :key="m.id" :class="['message', m.sender_id===userId?'message-self':'message-other']">
            <div class="message-bubble"><div class="message-text">{{ m.content }}</div><div class="message-time">{{ m.created_at }}</div></div>
          </div>
        </div>
        <div class="chat-input">
          <input v-model="newMsg" @keyup.enter="sendMsg" placeholder="输入消息..." class="form-control">
          <button class="btn btn-primary" @click="sendMsg"><i class="fas fa-paper-plane"></i></button>
        </div>
      </template>
    </div>
  </div>`,
  setup() {
    const contacts = ref([]);
    const selectedContact = ref(null);
    const messages = ref([]);
    const newMsg = ref('');
    const msgContainer = ref(null);
    const userId = ref(JSON.parse(localStorage.getItem('ai_edu_user')||'{}').id);
    const roleMap = { student:'学生', teacher:'教师', counselor:'辅导员', admin:'管理员' };
    const selectContact = async (c) => {
      selectedContact.value = c;
      try { messages.value = await api.chat.getMessages(c.id) || []; } catch(e) { messages.value = []; }
      nextTick(() => { if(msgContainer.value) msgContainer.value.scrollTop = msgContainer.value.scrollHeight; });
    };
    const sendMsg = async () => {
      if (!newMsg.value.trim() || !selectedContact.value) return;
      try {
        await api.chat.sendMessage({ receiver_id: selectedContact.value.id, content: newMsg.value });
        messages.value.push({ id: Date.now(), sender_id: userId.value, content: newMsg.value, created_at: new Date().toLocaleString() });
        newMsg.value = '';
        nextTick(() => { if(msgContainer.value) msgContainer.value.scrollTop = msgContainer.value.scrollHeight; });
      } catch(e) {}
    };
    onMounted(async () => { try { contacts.value = await api.chat.getContacts() || []; } catch(e) {} });
    return { contacts, selectedContact, messages, newMsg, msgContainer, userId, roleMap, selectContact, sendMsg };
  }
};

const StudentLeave = {
  template: `<div>
    <div class="card"><div class="card-header"><h3>申请请假</h3></div><div class="card-body">
      <form @submit.prevent="submitLeave" class="form">
        <div class="form-group"><label>类型</label><select v-model="form.type" class="form-control"><option value="leave">请假</option><option value="outing">离校外出</option></select></div>
        <div class="form-group"><label>理由</label><textarea v-model="form.reason" class="form-control" rows="3" placeholder="请输入请假理由"></textarea></div>
        <button type="submit" class="btn btn-primary">提交申请</button>
      </form>
    </div></div>
    <div class="card" style="margin-top:16px"><div class="card-header"><h3>申请记录</h3></div><div class="card-body">
      <div v-if="requests.length===0" class="empty-state">暂无记录</div>
      <div v-for="r in requests" :key="r.id" class="list-item">
        <div class="list-item-info"><div class="list-item-title">{{ r.type==='leave'?'请假':'离校外出' }}</div><div class="list-item-desc">{{ r.reason }} | {{ r.created_at }}</div></div>
        <span :class="['badge','badge-'+({pending:'warning',approved:'success',rejected:'danger'}[r.status])]">{{ {pending:'待审批',approved:'已批准',rejected:'已拒绝'}[r.status] }}</span>
      </div>
    </div></div>
  </div>`,
  setup() {
    const form = reactive({ type: 'leave', reason: '' });
    const requests = ref([]);
    const submitLeave = async () => {
      try { await api.request('/student/leave-request', { method:'POST', body: JSON.stringify(form) }); form.reason=''; loadRequests(); } catch(e) {}
    };
    const loadRequests = async () => { try { requests.value = await api.request('/counselor/leave-requests') || []; } catch(e) {} };
    onMounted(loadRequests);
    return { form, requests, submitLeave };
  }
};

const StudentSchedule = {
  template: `<div class="card"><div class="card-header"><h3>我的课表</h3></div><div class="card-body">
    <div class="schedule-grid">
      <div class="schedule-header"><div></div><div v-for="d in weekdays" :key="d">{{ d }}</div></div>
      <div v-for="h in timeSlots" :key="h" class="schedule-row">
        <div class="schedule-time">{{ h }}</div>
        <div v-for="d in 5" :key="d" class="schedule-cell">
          <div v-if="getCourse(d,h)" class="schedule-course">{{ getCourse(d,h).name }}</div>
        </div>
      </div>
    </div>
  </div></div>`,
  setup() {
    const courses = ref([]);
    const weekdays = ['周一','周二','周三','周四','周五'];
    const timeSlots = ['08:00','09:00','10:00','11:00','14:00','15:00','16:00','17:00'];
    const getCourse = (day, time) => { return courses.value.find(c => { const s = c.schedule||''; return s.includes(weekdays[day-1]) && s.includes(time); }); };
    onMounted(async () => { try { courses.value = await api.student.getCourses() || []; } catch(e) {} });
    return { courses, weekdays, timeSlots, getCourse };
  }
};

const StudentReminders = {
  template: `<div class="card"><div class="card-header"><h3>智能提醒</h3></div><div class="card-body">
    <div v-for="r in reminders" :key="r.id" :class="['reminder-item', 'reminder-'+r.type]">
      <div class="reminder-icon"><i :class="r.icon"></i></div>
      <div class="reminder-info"><div class="reminder-title">{{ r.title }}</div><div class="reminder-desc">{{ r.desc }}</div></div>
      <span class="badge" :class="'badge-'+r.severity">{{ r.time }}</span>
    </div>
  </div></div>`,
  setup() {
    const reminders = ref([
      { id:1, type:'warning', icon:'fas fa-exclamation-triangle', title:'数据结构作业即将到期', desc:'还有2天截止，请尽快提交', time:'2天', severity:'warning' },
      { id:2, type:'info', icon:'fas fa-file-powerpoint', title:'高等数学课件已上传', desc:'第三章：多元函数微分学', time:'1小时前', severity:'info' },
      { id:3, type:'danger', icon:'fas fa-alert', title:'学业预警', desc:'数据结构成绩低于60分警戒线', time:'紧急', severity:'danger' },
      { id:4, type:'success', icon:'fas fa-video', title:'课程回放推荐', desc:'算法设计与分析 - 第5节回放', time:'推荐', severity:'success' }
    ]);
    return { reminders };
  }
};


const TeacherDashboard = {
  template: `<div class="dashboard">
    <div class="stats-grid">
      <div class="stat-card" v-for="s in stats" :key="s.label">
        <div class="stat-icon" :style="{background:s.bg}"><i :class="s.icon"></i></div>
        <div class="stat-info"><div class="stat-value">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
      </div>
    </div>
    <div class="grid-2">
      <div class="card"><div class="card-header"><h3>今日课程</h3></div><div class="card-body">
        <div v-for="c in courses" :key="c.id" class="list-item">
          <div class="list-item-icon"><i class="fas fa-book"></i></div>
          <div class="list-item-info"><div class="list-item-title">{{ c.name }}</div><div class="list-item-desc">{{ c.schedule }}</div></div>
          <button class="btn btn-sm btn-primary" @click="$router.push('/teacher/course/'+c.id)">管理</button>
        </div>
      </div></div>
      <div class="card"><div class="card-header"><h3>AI教学建议</h3></div><div class="card-body">
        <div class="ai-suggestion"><div class="ai-icon"><i class="fas fa-robot"></i></div><div class="ai-content">
          <p>根据班级数据分析：</p><ul><li>建议加强数据结构中链表与树的讲解</li><li>班级签到率偏低，建议增加课堂互动</li><li>期中考试中算法题得分率仅45%</li></ul>
        </div></div>
      </div></div>
    </div>
  </div>`,
  setup() {
    const stats = ref([
      { label:'我的课程', value:'3', icon:'fas fa-book', bg:'var(--primary-bg)' },
      { label:'待批作业', value:'12', icon:'fas fa-tasks', bg:'var(--warning-bg)' },
      { label:'学生总数', value:'156', icon:'fas fa-users', bg:'var(--success-bg)' },
      { label:'平均签到率', value:'92%', icon:'fas fa-check-circle', bg:'var(--danger-bg)' }
    ]);
    const courses = ref([]);
    onMounted(async () => { try { courses.value = await api.teacher.getCourses() || []; } catch(e) {} });
    return { stats, courses };
  }
};

const TeacherCourses = {
  template: `<div class="card"><div class="card-header"><h3>我的课程</h3></div><div class="card-body">
    <div class="grid-3">
      <div v-for="c in courses" :key="c.id" class="course-card" @click="$router.push('/teacher/course/'+c.id)">
        <div class="course-card-header" style="background:var(--primary)"><i class="fas fa-chalkboard-teacher"></i></div>
        <div class="course-card-body"><h4>{{ c.name }}</h4><p>{{ c.class_name }} | {{ c.schedule }}</p></div>
      </div>
    </div>
  </div></div>`,
  setup() {
    const courses = ref([]);
    onMounted(async () => { try { courses.value = await api.teacher.getCourses() || []; } catch(e) {} });
    return { courses };
  }
};

const TeacherCourseDetail = {
  template: `<div>
    <div class="card"><div class="card-header"><h3>{{ course.name || '课程管理' }}</h3>
      <div class="tabs">
        <button v-for="t in tabs" :key="t.key" :class="['tab',tab===t.key?'active':'']" @click="tab=t.key"><i :class="t.icon"></i> {{ t.label }}</button>
      </div></div>
      <div class="card-body">
        <div v-if="tab==='courseware'">
          <button class="btn btn-primary btn-sm" @click="uploadCourseware"><i class="fas fa-upload"></i> 上传课件</button>
          <div v-for="c in courseware" :key="c.id" class="list-item" style="margin-top:8px">
            <div class="list-item-icon"><i class="fas fa-file-pdf" style="color:var(--danger)"></i></div>
            <div class="list-item-info"><div class="list-item-title">{{ c.title }}</div><div class="list-item-desc">{{ c.upload_time }}</div></div>
          </div>
        </div>
        <div v-if="tab==='assignments'">
          <button class="btn btn-primary btn-sm" @click="$router.push('/teacher/assignments')"><i class="fas fa-plus"></i> 布置作业</button>
          <div v-for="a in assignments" :key="a.id" class="list-item" style="margin-top:8px">
            <div class="list-item-info"><div class="list-item-title">{{ a.title }}</div><div class="list-item-desc">截止: {{ a.deadline }}</div></div>
            <button class="btn btn-sm btn-outline" @click="$router.push('/teacher/grading/'+a.id)">批改</button>
          </div>
        </div>
        <div v-if="tab==='attendance'">
          <button class="btn btn-primary btn-sm" @click="startAttendance"><i class="fas fa-qrcode"></i> 发起签到</button>
          <div v-if="attendanceCode" class="attendance-code-box">
            <div class="attendance-code">{{ attendanceCode }}</div>
            <p>请学生在8秒内输入此动态码完成签到</p>
          </div>
        </div>
        <div v-if="tab==='analysis'">
          <button class="btn btn-primary btn-sm" @click="loadAnalysis"><i class="fas fa-chart-bar"></i> 加载班级分析</button>
          <div v-if="analysis" style="margin-top:16px">
            <div class="stats-grid">
              <div class="stat-card"><div class="stat-info"><div class="stat-value">{{ analysis.avg_score }}</div><div class="stat-label">平均分</div></div></div>
              <div class="stat-card"><div class="stat-info"><div class="stat-value">{{ analysis.attendance_rate }}%</div><div class="stat-label">签到率</div></div></div>
              <div class="stat-card"><div class="stat-info"><div class="stat-value">{{ analysis.submit_rate }}%</div><div class="stat-label">作业提交率</div></div></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>`,
  setup() {
    const route = VueRouter.useRoute();
    const tab = ref('courseware');
    const course = ref({});
    const courseware = ref([]);
    const assignments = ref([]);
    const attendanceCode = ref('');
    const analysis = ref(null);
    const tabs = [
      { key:'courseware', label:'课件', icon:'fas fa-file-powerpoint' },
      { key:'assignments', label:'作业', icon:'fas fa-tasks' },
      { key:'attendance', label:'签到', icon:'fas fa-qrcode' },
      { key:'analysis', label:'分析', icon:'fas fa-chart-bar' }
    ];
    const uploadCourseware = () => { alert('课件上传功能演示'); };
    const startAttendance = () => {
      attendanceCode.value = Math.floor(100000 + Math.random() * 900000).toString();
      setTimeout(() => { attendanceCode.value = ''; }, 8000);
    };
    const loadAnalysis = async () => {
      try { analysis.value = await api.teacher.getClassAnalysis(route.params.id); } catch(e) { analysis.value = { avg_score:78.5, attendance_rate:92, submit_rate:88 }; }
    };
    onMounted(async () => {
      const id = route.params.id;
      try { const c = await api.teacher.getCourses(); course.value = (c||[]).find(x=>x.id==id)||{}; } catch(e) {}
      try { assignments.value = await api.teacher.getAssignments ? [] : []; } catch(e) {}
    });
    return { tab, course, courseware, assignments, attendanceCode, analysis, tabs, uploadCourseware, startAttendance, loadAnalysis };
  }
};

const TeacherAttendance = {
  template: `<div class="card"><div class="card-header"><h3>签到管理</h3>
    <button class="btn btn-primary btn-sm" @click="startCode"><i class="fas fa-qrcode"></i> 发起签到</button></div>
    <div class="card-body">
    <div v-if="code" class="attendance-code-box"><div class="attendance-code">{{ code }}</div><p>8秒实时动态码，请学生尽快输入</p></div>
    <div class="table-wrapper"><table class="table"><thead><tr><th>学生</th><th>状态</th><th>签到时间</th></tr></thead>
    <tbody><tr v-for="a in records" :key="a.id"><td>{{ a.student_name }}</td>
    <td><span :class="['badge','badge-'+(a.status==='present'?'success':'danger')]">{{ a.status==='present'?'已签到':'缺勤' }}</span></td>
    <td>{{ a.check_in_time || '-' }}</td></tr></tbody></table></div>
  </div></div>`,
  setup() {
    const code = ref('');
    const records = ref([]);
    const startCode = () => { code.value = Math.floor(100000+Math.random()*900000).toString(); setTimeout(()=>code.value='',8000); };
    return { code, records, startCode };
  }
};

const TeacherGrading = {
  template: `<div class="card"><div class="card-header"><h3>作业批改</h3></div><div class="card-body">
    <div v-if="submissions.length===0" class="empty-state">暂无待批改作业</div>
    <div v-for="s in submissions" :key="s.id" class="grading-item">
      <div class="grading-header"><strong>{{ s.student_name }}</strong><span>{{ s.submit_time }}</span></div>
      <div class="grading-content">{{ s.content }}</div>
      <div class="grading-form">
        <input v-model="s.score" type="number" class="form-control" style="width:100px" placeholder="分数">
        <input v-model="s.feedback" class="form-control" placeholder="批改反馈">
        <button class="btn btn-primary btn-sm" @click="grade(s)">提交</button>
      </div>
    </div>
  </div></div>`,
  setup() {
    const submissions = ref([]);
    const grade = async (s) => { try { await api.teacher.gradeSubmission({ submission_id: s.id, score: s.score, feedback: s.feedback }); s.graded = true; } catch(e) {} };
    return { submissions, grade };
  }
};

const TeacherExamAnalysis = {
  template: `<div class="card"><div class="card-header"><h3>考试分析</h3></div><div class="card-body">
    <div v-if="!analysis" class="empty-state">选择考试查看AI分析</div>
    <div v-else>
      <div class="stats-grid"><div class="stat-card"><div class="stat-info"><div class="stat-value">{{ analysis.avg_score }}</div><div class="stat-label">平均分</div></div></div>
      <div class="stat-card"><div class="stat-info"><div class="stat-value">{{ analysis.pass_rate }}%</div><div class="stat-label">及格率</div></div></div>
      <div class="stat-card"><div class="stat-info"><div class="stat-value">{{ analysis.excellent_rate }}%</div><div class="stat-label">优秀率</div></div></div></div>
      <div class="ai-suggestion" style="margin-top:16px"><div class="ai-icon"><i class="fas fa-robot"></i></div><div class="ai-content"><p>AI教学建议：</p><ul><li v-for="s in analysis.suggestions" :key="s">{{ s }}</li></ul></div></div>
    </div>
  </div></div>`,
  setup() {
    const analysis = ref(null);
    onMounted(async () => {
      try { analysis.value = await api.agents.examAnalysis(1); } catch(e) {
        analysis.value = { avg_score:75.3, pass_rate:82, excellent_rate:15, suggestions:['建议加强算法复杂度分析的讲解','链表操作需要更多练习题','可以增加课堂编程练习环节'] };
      }
    });
    return { analysis };
  }
};

const TeacherAssignments = {
  template: `<div class="card"><div class="card-header"><h3>布置作业</h3></div><div class="card-body">
    <form @submit.prevent="createAssignment" class="form">
      <div class="form-group"><label>课程</label><select v-model="form.course_id" class="form-control"><option v-for="c in courses" :key="c.id" :value="c.id">{{ c.name }}</option></select></div>
      <div class="form-group"><label>标题</label><input v-model="form.title" class="form-control" placeholder="作业标题"></div>
      <div class="form-group"><label>内容</label><textarea v-model="form.content" class="form-control" rows="5" placeholder="作业内容"></textarea></div>
      <div class="form-group"><label>截止时间</label><input v-model="form.deadline" type="datetime-local" class="form-control"></div>
      <button type="submit" class="btn btn-primary">发布作业</button>
    </form>
  </div></div>`,
  setup() {
    const form = reactive({ course_id:'', title:'', content:'', deadline:'' });
    const courses = ref([]);
    const createAssignment = async () => { try { await api.teacher.createAssignment(form); alert('作业发布成功'); } catch(e) {} };
    onMounted(async () => { try { courses.value = await api.teacher.getCourses() || []; } catch(e) {} });
    return { form, courses, createAssignment };
  }
};


const CounselorDashboard = {
  template: `<div class="dashboard">
    <div class="stats-grid">
      <div class="stat-card"><div class="stat-icon" style="background:var(--warning-bg)"><i class="fas fa-file-alt"></i></div><div class="stat-info"><div class="stat-value">{{ pendingCount }}</div><div class="stat-label">待审批请假</div></div></div>
      <div class="stat-card"><div class="stat-icon" style="background:var(--danger-bg)"><i class="fas fa-exclamation-triangle"></i></div><div class="stat-info"><div class="stat-value">{{ alertCount }}</div><div class="stat-label">学业预警</div></div></div>
      <div class="stat-card"><div class="stat-icon" style="background:var(--primary-bg)"><i class="fas fa-users"></i></div><div class="stat-info"><div class="stat-value">{{ studentCount }}</div><div class="stat-label">学生总数</div></div></div>
    </div>
    <div class="card"><div class="card-header"><h3>待处理事项</h3></div><div class="card-body">
      <div v-for="r in pendingRequests" :key="r.id" class="list-item">
        <div class="list-item-info"><div class="list-item-title">{{ r.student_name }} - {{ r.type==='leave'?'请假':'离校' }}</div><div class="list-item-desc">{{ r.reason }}</div></div>
        <div><button class="btn btn-success btn-sm" @click="approve(r.id,'approved')">批准</button> <button class="btn btn-danger btn-sm" @click="approve(r.id,'rejected')">拒绝</button></div>
      </div>
    </div></div>
  </div>`,
  setup() {
    const pendingRequests = ref([]);
    const pendingCount = ref(0);
    const alertCount = ref(3);
    const studentCount = ref(60);
    const approve = async (id, status) => { try { await api.counselor.approveLeave(id, status); pendingRequests.value = pendingRequests.value.filter(r=>r.id!==id); pendingCount.value--; } catch(e) {} };
    onMounted(async () => { try { pendingRequests.value = await api.counselor.getLeaveRequests('pending') || []; pendingCount.value = pendingRequests.value.length; } catch(e) {} });
    return { pendingRequests, pendingCount, alertCount, studentCount, approve };
  }
};

const CounselorLeaveManagement = {
  template: `<div class="card"><div class="card-header"><h3>请假管理</h3>
    <div class="tabs"><button v-for="t in tabs" :key="t.key" :class="['tab',filter===t.key?'active':'']" @click="filter=t.key;load()">{{ t.label }}</button></div></div>
    <div class="card-body">
    <div v-if="requests.length===0" class="empty-state">暂无记录</div>
    <div v-for="r in requests" :key="r.id" class="list-item">
      <div class="list-item-info"><div class="list-item-title">{{ r.student_name }} ({{ r.class_name }})</div><div class="list-item-desc">{{ r.type==='leave'?'请假':'离校外出' }}: {{ r.reason }} | {{ r.created_at }}</div></div>
      <div v-if="r.status==='pending'"><button class="btn btn-success btn-sm" @click="act(r.id,'approved')">批准</button> <button class="btn btn-danger btn-sm" @click="act(r.id,'rejected')">拒绝</button></div>
      <span v-else :class="['badge','badge-'+(r.status==='approved'?'success':'danger')]">{{ r.status==='approved'?'已批准':'已拒绝' }}</span>
    </div>
  </div></div>`,
  setup() {
    const filter = ref('all');
    const requests = ref([]);
    const tabs = [{key:'all',label:'全部'},{key:'pending',label:'待审批'},{key:'approved',label:'已批准'},{key:'rejected',label:'已拒绝'}];
    const load = async () => { try { requests.value = await api.counselor.getLeaveRequests(filter.value==='all'?null:filter.value) || []; } catch(e) {} };
    const act = async (id, status) => { try { await api.counselor.approveLeave(id, status); load(); } catch(e) {} };
    onMounted(load);
    return { filter, requests, tabs, load, act };
  }
};

const CounselorStudentGrades = {
  template: `<div class="card"><div class="card-header"><h3>学生成绩总览</h3></div><div class="card-body">
    <div v-if="students.length===0" class="empty-state">暂无数据</div>
    <div class="table-wrapper"><table class="table"><thead><tr><th>姓名</th><th>班级</th><th>平均分</th><th>考试数</th><th>状态</th></tr></thead>
    <tbody><tr v-for="s in students" :key="s.id"><td>{{ s.name }}</td><td>{{ s.class_name }}</td><td>{{ s.average_score }}</td><td>{{ s.exams.length }}</td>
    <td><span :class="['badge',s.average_score>=60?'badge-success':'badge-danger']">{{ s.average_score>=60?'正常':'预警' }}</span></td></tr></tbody></table></div>
  </div></div>`,
  setup() {
    const students = ref([]);
    onMounted(async () => { try { students.value = await api.counselor.getStudentGrades('计算机2024A') || []; } catch(e) {} });
    return { students };
  }
};

const CounselorClassOverview = {
  template: `<div>
    <div class="stats-grid">
      <div class="stat-card"><div class="stat-info"><div class="stat-value">{{ overview.student_count||0 }}</div><div class="stat-label">学生总数</div></div></div>
      <div class="stat-card"><div class="stat-info"><div class="stat-value">{{ overview.pending_leaves||0 }}</div><div class="stat-label">待审请假</div></div></div>
    </div>
    <div class="card" style="margin-top:16px"><div class="card-header"><h3>班级公告</h3></div><div class="card-body">
      <div v-for="a in overview.announcements||[]" :key="a.id" class="list-item">
        <div class="list-item-info"><div class="list-item-title">{{ a.content }}</div><div class="list-item-desc">{{ a.author_name }} | {{ a.created_at }}</div></div>
      </div>
      <div v-if="!overview.announcements?.length" class="empty-state">暂无公告</div>
    </div></div>
  </div>`,
  setup() {
    const overview = ref({});
    onMounted(async () => { try { overview.value = await api.counselor.getClassOverview('计算机2024A') || {}; } catch(e) {} });
    return { overview };
  }
};


const AdminDashboard = {
  template: `<div>
    <div class="stat-cards">
      <div class="stat-card"><div class="stat-icon" style="background:var(--primary-bg)"><i class="fas fa-microchip"></i></div><div class="stat-info"><div class="stat-value">{{ server.cpu?.percent||0 }}%</div><div class="stat-label">CPU使用率</div><div class="stat-indicator" :class="getUsageClass(server.cpu?.percent||0)"></div></div>
      <div class="stat-card"><div class="stat-icon" style="background:var(--warning-bg)"><i class="fas fa-memory"></i></div><div class="stat-info"><div class="stat-value">{{ server.memory?.percent||0 }}%</div><div class="stat-label">内存使用率</div><div class="stat-indicator" :class="getUsageClass(server.memory?.percent||0)"></div></div>
      <div class="stat-card"><div class="stat-icon" style="background:var(--danger-bg)"><i class="fas fa-hdd"></i></div><div class="stat-info"><div class="stat-value">{{ server.disk?.percent||0 }}%</div><div class="stat-label">磁盘使用率</div><div class="stat-indicator" :class="getUsageClass(server.disk?.percent||0)"></div></div>
      <div class="stat-card"><div class="stat-icon" style="background:var(--success-bg)"><i class="fas fa-clock"></i></div><div class="stat-info"><div class="stat-value">{{ server.uptime_hours||0 }}h</div><div class="stat-label">运行时长</div></div>
    </div>
    <div class="grid-2">
      <div class="card"><div class="card-header"><h3>系统统计 <span class="live-badge">实时</span></h3></div><div class="card-body">
        <div class="list-item"><div class="list-item-info"><div class="list-item-title">总用户数</div></div><span>{{ stats.total_users||0 }}</span></div>
        <div class="list-item"><div class="list-item-info"><div class="list-item-title">课程数</div></div><span>{{ stats.courses||0 }}</span></div>
        <div class="list-item"><div class="list-item-info"><div class="list-item-title">消息数</div></div><span>{{ stats.messages||0 }}</span></div>
        <div class="list-item"><div class="list-item-info"><div class="list-item-title">今日活跃</div></div><span>{{ stats.active_today||0 }}</span></div>
      </div></div>
      <div class="card"><div class="card-header"><h3>Bug报告</h3></div><div class="card-body">
        <div v-for="b in bugs" :key="b.id" class="list-item">
          <div class="list-item-info"><div class="list-item-title">{{ b.title }}</div><div class="list-item-desc">{{ b.reported_by }} | {{ b.created_at }}</div></div>
          <span :class="['badge','badge-'+({high:'danger',medium:'warning',low:'success'}[b.severity])]">{{ b.severity }}</span>
        </div>
      </div></div>
    </div>
  </div>`,
  setup() {
    const server = ref({});
    const stats = ref({});
    const bugs = ref([]);
    let refreshInterval = null;
    
    const getUsageClass = (percent) => {
      if (percent >= 90) return 'danger';
      if (percent >= 70) return 'warning';
      return 'success';
    };
    
    const loadData = async () => {
      try { 
        server.value = await api.admin.getServerStatus() || { cpu:{percent:35}, memory:{percent:62}, disk:{percent:45}, uptime_hours:120 }; 
      } catch(e) { 
        server.value = { cpu:{percent:35 + Math.floor(Math.random() * 20)}, memory:{percent:62 + Math.floor(Math.random() * 15)}, disk:{percent:45 + Math.floor(Math.random() * 10)}, uptime_hours:120 }; 
      }
      try { stats.value = await api.admin.getSystemStats() || {}; } catch(e) {}
    };
    
    onMounted(async () => {
      await loadData();
      try { bugs.value = await api.admin.getBugReports() || []; } catch(e) {}
      
      
      refreshInterval = setInterval(loadData, 5000);
    });
    
    onUnmounted(() => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    });
    
    return { server, stats, bugs, getUsageClass };
  }
};

const AdminUsers = {
  template: `<div class="card"><div class="card-header"><h3>用户管理</h3>
    <select v-model="roleFilter" @change="loadUsers" class="form-control" style="width:150px"><option value="">全部角色</option><option value="student">学生</option><option value="teacher">教师</option><option value="counselor">辅导员</option><option value="admin">管理员</option></select></div>
    <div class="card-body">
    <div class="table-wrapper"><table class="table"><thead><tr><th>ID</th><th>账号</th><th>姓名</th><th>角色</th><th>班级</th><th>操作</th></tr></thead>
    <tbody><tr v-for="u in users" :key="u.id"><td>{{ u.id }}</td><td>{{ u.username }}</td><td>{{ u.name }}</td>
    <td><span class="badge badge-primary">{{ roleMap[u.role] }}</span></td><td>{{ u.class_name||'-' }}</td>
    <td><button class="btn btn-sm btn-outline">编辑</button></td></tr></tbody></table></div>
  </div></div>`,
  setup() {
    const users = ref([]);
    const roleFilter = ref('');
    const roleMap = { student:'学生', teacher:'教师', counselor:'辅导员', admin:'管理员' };
    const loadUsers = async () => { try { users.value = await api.admin.getAllUsers(roleFilter.value||null) || []; } catch(e) {} };
    onMounted(loadUsers);
    return { users, roleFilter, roleMap, loadUsers };
  }
};

const AdminSystem = {
  template: `<div class="card"><div class="card-header"><h3>系统监控</h3></div><div class="card-body">
    <div class="grid-2">
      <div><h4>CPU使用率</h4><div class="progress-bar"><div class="progress-fill" :style="{width:server.cpu?.percent+'%',background:'var(--primary)'}"></div></div><span>{{ server.cpu?.percent }}%</span></div>
      <div><h4>内存使用率</h4><div class="progress-bar"><div class="progress-fill" :style="{width:server.memory?.percent+'%',background:'var(--warning)'}"></div></div><span>{{ server.memory?.used_gb }}GB / {{ server.memory?.total_gb }}GB</span></div>
    </div>
  </div></div>`,
  setup() {
    const server = ref({});
    onMounted(async () => { try { server.value = await api.admin.getServerStatus() || {}; } catch(e) {} });
    return { server };
  }
};


const AIAnalysis = {
  template: `<div>
    <div class="card">
      <div class="card-header"><h3><i class="fas fa-robot"></i> AI分析中心</h3></div>
      <div class="card-body">
        <div class="ai-workflow">
          <div class="workflow-title">多智能体协作流程</div>
          <div class="workflow-diagram">
            <div class="workflow-agent"><div class="agent-icon" style="background:var(--primary)"><i class="fas fa-user-graduate"></i></div><span>学情分析Agent</span></div>
            <div class="workflow-arrow">→</div>
            <div class="workflow-agent"><div class="agent-icon" style="background:var(--success)"><i class="fas fa-lightbulb"></i></div><span>资源生成Agent</span></div>
            <div class="workflow-arrow">→</div>
            <div class="workflow-agent"><div class="agent-icon" style="background:var(--warning)"><i class="fas fa-chalkboard-teacher"></i></div><span>教学优化Agent</span></div>
            <div class="workflow-arrow">→</div>
            <div class="workflow-agent"><div class="agent-icon" style="background:var(--danger)"><i class="fas fa-file-alt"></i></div><span>考试分析Agent</span></div>
          </div>
        </div>
        <div class="tabs" style="margin-top:24px">
          <button v-for="t in tabs" :key="t.key" :class="['tab',activeTab===t.key?'active':'']" @click="activeTab=t.key"><i :class="t.icon"></i> {{ t.label }}</button>
        </div>
        <div style="margin-top:16px">
          <div v-if="activeTab==='student'">
            <button class="btn btn-primary" @click="runStudentAnalysis"><i class="fas fa-play"></i> 运行学情分析</button>
            <div v-if="studentResult" class="ai-result" style="margin-top:16px">
              <h4>分析结果</h4>
              <div class="stats-grid">
                <div class="stat-card"><div class="stat-info"><div class="stat-value">{{ studentResult.risk_level }}</div><div class="stat-label">风险等级</div></div></div>
                <div class="stat-card"><div class="stat-info"><div class="stat-value">{{ studentResult.predicted_score }}</div><div class="stat-label">预测分数</div></div></div>
                <div class="stat-card"><div class="stat-info"><div class="stat-value">{{ studentResult.learning_style }}</div><div class="stat-label">学习风格</div></div></div>
              </div>
              <div style="margin-top:12px"><strong>薄弱知识点：</strong><span v-for="w in studentResult.weak_points" :key="w" class="tag tag-danger" style="margin:2px">{{ w }}</span></div>
              <div style="margin-top:8px"><strong>建议：</strong><ul><li v-for="r in studentResult.recommendations" :key="r">{{ r }}</li></ul></div>
            </div>
          </div>
          <div v-if="activeTab==='resource'">
            <button class="btn btn-primary" @click="runResourceGen"><i class="fas fa-magic"></i> 生成个性化资源</button>
            <div v-if="resourceResult" class="grid-3" style="margin-top:16px">
              <div v-for="r in resourceResult" :key="r.title" class="resource-card">
                <h4>{{ r.title }}</h4><p>{{ r.description }}</p>
              </div>
            </div>
          </div>
          <div v-if="activeTab==='exam'">
            <button class="btn btn-primary" @click="runExamAnalysis"><i class="fas fa-chart-bar"></i> 运行考试分析</button>
            <div v-if="examResult" style="margin-top:16px">
              <div class="stats-grid">
                <div class="stat-card"><div class="stat-info"><div class="stat-value">{{ examResult.avg_score }}</div><div class="stat-label">平均分</div></div></div>
                <div class="stat-card"><div class="stat-info"><div class="stat-value">{{ examResult.pass_rate }}%</div><div class="stat-label">及格率</div></div></div>
              </div>
              <div class="ai-suggestion" style="margin-top:12px"><div class="ai-icon"><i class="fas fa-robot"></i></div><div class="ai-content"><ul><li v-for="s in examResult.suggestions" :key="s">{{ s }}</li></ul></div></div>
            </div>
          </div>
          <div v-if="activeTab==='plan'">
            <button class="btn btn-primary" @click="runLearningPlan"><i class="fas fa-calendar-alt"></i> 生成学习计划</button>
            <div v-if="planResult" style="margin-top:16px">
              <div v-for="(week, i) in planResult.weekly_plan||[]" :key="i" class="plan-day">
                <h4>{{ week.day }}</h4><ul><li v-for="t in week.tasks" :key="t">{{ t }}</li></ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>`,
  setup() {
    const activeTab = ref('student');
    const studentResult = ref(null);
    const resourceResult = ref(null);
    const examResult = ref(null);
    const planResult = ref(null);
    const tabs = [
      { key:'student', label:'学情分析', icon:'fas fa-user-graduate' },
      { key:'resource', label:'资源生成', icon:'fas fa-magic' },
      { key:'exam', label:'考试分析', icon:'fas fa-chart-bar' },
      { key:'plan', label:'学习计划', icon:'fas fa-calendar-alt' }
    ];
    const runStudentAnalysis = async () => { try { studentResult.value = await api.agents.analyzeStudent({student_id:1}); } catch(e) { studentResult.value = {risk_level:'中等',predicted_score:72,learning_style:'视觉型',weak_points:['链表操作','二叉树遍历'],recommendations:['每天练习2道链表题','观看树结构教学视频']}; } };
    const runResourceGen = async () => { try { const r = await api.agents.generateResources({student_id:1,course_id:1}); resourceResult.value = r?.resources||[]; } catch(e) { resourceResult.value = [{title:'链表专项练习',description:'5道针对链表操作的练习题'},{title:'二叉树遍历视频',description:'前中后序遍历动画讲解'}]; } };
    const runExamAnalysis = async () => { try { examResult.value = await api.agents.examAnalysis(1); } catch(e) { examResult.value = {avg_score:75.3,pass_rate:82,suggestions:['加强算法复杂度讲解','增加编程练习']}; } };
    const runLearningPlan = async () => { try { planResult.value = await api.agents.generateLearningPlan({student_id:1,course_id:1}); } catch(e) { planResult.value = {weekly_plan:[{day:'周一',tasks:['复习链表基础','完成3道练习题']},{day:'周二',tasks:['学习二叉树遍历','观看教学视频']},{day:'周三',tasks:['综合练习','错题回顾']}]}; } };
    return { activeTab, studentResult, resourceResult, examResult, planResult, tabs, runStudentAnalysis, runResourceGen, runExamAnalysis, runLearningPlan };
  }
};



const routes = [
  { path: '/', redirect: '/student/dashboard' },
  { path: '/student/dashboard', component: StudentDashboard, meta: { title: '学生首页' } },
  { path: '/student/courses', component: StudentCourses, meta: { title: '我的课程' } },
  { path: '/student/course/:id', component: StudentCourseDetail, meta: { title: '课程详情' } },
  { path: '/student/assignments', component: StudentAssignments, meta: { title: '我的作业' } },
  { path: '/student/exams', component: StudentExams, meta: { title: '考试成绩' } },
  { path: '/student/resources', component: StudentResources, meta: { title: '学习资源' } },
  { path: '/student/chat', component: StudentChat, meta: { title: '聊天' } },
  { path: '/student/leave', component: StudentLeave, meta: { title: '请假申请' } },
  { path: '/student/schedule', component: StudentSchedule, meta: { title: '我的课表' } },
  { path: '/student/reminders', component: StudentReminders, meta: { title: '智能提醒' } },
  { path: '/teacher/dashboard', component: TeacherDashboard, meta: { title: '教师首页' } },
  { path: '/teacher/courses', component: TeacherCourses, meta: { title: '我的课程' } },
  { path: '/teacher/course/:id', component: TeacherCourseDetail, meta: { title: '课程管理' } },
  { path: '/teacher/attendance', component: TeacherAttendance, meta: { title: '签到管理' } },
  { path: '/teacher/grading', component: TeacherGrading, meta: { title: '作业批改' } },
  { path: '/teacher/exam-analysis', component: TeacherExamAnalysis, meta: { title: '考试分析' } },
  { path: '/teacher/assignments', component: TeacherAssignments, meta: { title: '布置作业' } },
  { path: '/counselor/dashboard', component: CounselorDashboard, meta: { title: '辅导员首页' } },
  { path: '/counselor/leave', component: CounselorLeaveManagement, meta: { title: '请假管理' } },
  { path: '/counselor/grades', component: CounselorStudentGrades, meta: { title: '学生成绩' } },
  { path: '/counselor/overview', component: CounselorClassOverview, meta: { title: '班级总览' } },
  { path: '/admin/dashboard', component: AdminDashboard, meta: { title: '管理首页' } },
  { path: '/admin/users', component: AdminUsers, meta: { title: '用户管理' } },
  { path: '/admin/system', component: AdminSystem, meta: { title: '系统监控' } },
  { path: '/ai/analysis', component: AIAnalysis, meta: { title: 'AI分析中心' } }
];

const router = createRouter({ history: createWebHashHistory(), routes });



function getCookie(name) {
  const nameEQ = name + "=";
  const ca = document.cookie.split(';');
  for(let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
  }
  return null;
}


function checkLoginStatusBeforeMount() {
  const token = getCookie('ai_edu_token');
  const userStr = getCookie('ai_edu_user');
  
  if (token && userStr) {
    try {
      const user = JSON.parse(decodeURIComponent(userStr));
      return { isLoggedIn: true, currentUser: user };
    } catch (e) {
      console.error('Failed to parse user from cookie:', e);
    }
  }
  return { isLoggedIn: false, currentUser: null };
}


const preCheckResult = checkLoginStatusBeforeMount();


if (!preCheckResult.isLoggedIn) {
  window.location.href = '/';
}

const app = createApp({
  setup() {
    
    const isLoggedIn = ref(preCheckResult.isLoggedIn);
    const currentUser = ref(preCheckResult.currentUser);
    const sidebarCollapsed = ref(false);
    const currentTime = ref('');
    const toast = reactive({ show: false, message: '', type: 'info' });

    const roleLabel = computed(() => {
      const map = { student: '学生', teacher: '教师', counselor: '辅导员', admin: '管理员' };
      return map[currentUser.value?.role] || '';
    });

    const menuItems = computed(() => {
      const role = currentUser.value?.role;
      const prefix = '/' + role;
      const menus = {
        student: [
          { path: '/student/dashboard', label: '首页', icon: 'fas fa-home' },
          { path: '/student/courses', label: '我的课程', icon: 'fas fa-book' },
          { path: '/student/assignments', label: '我的作业', icon: 'fas fa-tasks' },
          { path: '/student/exams', label: '考试成绩', icon: 'fas fa-chart-line' },
          { path: '/student/resources', label: '学习资源', icon: 'fas fa-lightbulb' },
          { path: '/student/schedule', label: '我的课表', icon: 'fas fa-calendar' },
          { path: '/student/chat', label: '聊天', icon: 'fas fa-comments' },
          { path: '/student/leave', label: '请假申请', icon: 'fas fa-file-alt' },
          { path: '/student/reminders', label: '智能提醒', icon: 'fas fa-bell', badge: 3 },
          { path: '/ai/analysis', label: 'AI分析中心', icon: 'fas fa-robot' }
        ],
        teacher: [
          { path: '/teacher/dashboard', label: '首页', icon: 'fas fa-home' },
          { path: '/teacher/courses', label: '我的课程', icon: 'fas fa-book' },
          { path: '/teacher/attendance', label: '签到管理', icon: 'fas fa-qrcode' },
          { path: '/teacher/assignments', label: '布置作业', icon: 'fas fa-plus' },
          { path: '/teacher/grading', label: '作业批改', icon: 'fas fa-check' },
          { path: '/teacher/exam-analysis', label: '考试分析', icon: 'fas fa-chart-bar' },
          { path: '/student/chat', label: '聊天', icon: 'fas fa-comments' },
          { path: '/ai/analysis', label: 'AI分析中心', icon: 'fas fa-robot' }
        ],
        counselor: [
          { path: '/counselor/dashboard', label: '首页', icon: 'fas fa-home' },
          { path: '/counselor/leave', label: '请假管理', icon: 'fas fa-file-alt' },
          { path: '/counselor/grades', label: '学生成绩', icon: 'fas fa-chart-line' },
          { path: '/counselor/overview', label: '班级总览', icon: 'fas fa-users' },
          { path: '/student/chat', label: '聊天', icon: 'fas fa-comments' }
        ],
        admin: [
          { path: '/admin/dashboard', label: '管理首页', icon: 'fas fa-home' },
          { path: '/admin/users', label: '用户管理', icon: 'fas fa-users-cog' },
          { path: '/admin/system', label: '系统监控', icon: 'fas fa-server' },
          { path: '/student/chat', label: '聊天', icon: 'fas fa-comments' }
        ]
      };
      return menus[role] || [];
    });

    const currentPageTitle = computed(() => {
      return router.currentRoute.value.meta?.title || 'AI教育平台';
    });

    const toastIcon = computed(() => {
      const map = { success: 'fas fa-check-circle', error: 'fas fa-times-circle', warning: 'fas fa-exclamation-circle', info: 'fas fa-info-circle' };
      return map[toast.type] || map.info;
    });

    const showToast = (message, type = 'info') => {
      toast.message = message;
      toast.type = type;
      toast.show = true;
      setTimeout(() => toast.show = false, 3000);
    };

    const handleLogout = () => {
      api.removeToken();
      document.cookie = 'ai_edu_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
      document.cookie = 'ai_edu_user=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
      try {
        sessionStorage.removeItem('ai_edu_token');
        sessionStorage.removeItem('ai_edu_user');
      } catch (e) {
        console.warn('sessionStorage blocked');
      }
      isLoggedIn.value = false;
      currentUser.value = null;
      window.location.href = '/';
    };

    
    const updateTime = () => {
      currentTime.value = new Date().toLocaleString('zh-CN');
    };
    setInterval(updateTime, 1000);
    updateTime();

    
    onMounted(() => {
      
      const token = getCookie('ai_edu_token');
      const userStr = getCookie('ai_edu_user');
      
      if (token && userStr) {
        try {
          const user = JSON.parse(decodeURIComponent(userStr));
          isLoggedIn.value = true;
          currentUser.value = user;
          console.log('[DEBUG] Logged in from cookie:', user);
          
          const currentPath = router.currentRoute.value.path;
          if (currentPath === '/' || currentPath === '') {
            router.push('/' + user.role + '/dashboard');
          }
        } catch (e) {
          console.error('[DEBUG] Failed to parse user from cookie:', e);
        }
      }
    });

    return {
      isLoggedIn, currentUser, sidebarCollapsed, currentTime,
      roleLabel, menuItems, currentPageTitle, toast, toastIcon, handleLogout
    };
  }
});

app.use(router);

app.mount('#app');
console.log('[DEBUG] Vue app mounted successfully');


const initialLoading = document.getElementById('initialLoading');
const vueContent = document.getElementById('vueContent');
if (initialLoading) initialLoading.style.display = 'none';
if (vueContent) vueContent.style.display = 'block';


document.addEventListener('click', function(e) {
  if (e.target.closest('.login-form')) {
    console.log('[DEBUG] Click inside login form:', e.target);
  }
});
