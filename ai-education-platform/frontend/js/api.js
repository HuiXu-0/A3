

const API_BASE = window.location.origin + '/api';

class ApiService {
  constructor() {
    this.baseURL = API_BASE;
    this.tokenKey = 'ai_edu_token';
    this.userKey = 'ai_edu_user';
    this.memoryStorage = {};
  }

  _setCookie(name, value, days = 1) {
    try {
      const date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      const expires = "; expires=" + date.toUTCString();
      document.cookie = name + "=" + (value || "") + expires + "; path=/";
      return true;
    } catch (e) {
      return false;
    }
  }

  _getCookie(name) {
    try {
      const nameEQ = name + "=";
      const ca = document.cookie.split(';');
      for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  _deleteCookie(name) {
    try {
      document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    } catch (e) {
      
    }
  }

  _safeStorageGet(key) {
    let value = this._getCookie(key);
    if (value) return value;
    
    try {
      value = localStorage.getItem(key);
      if (value) return value;
    } catch (e) {
      
    }
    
    try {
      value = sessionStorage.getItem(key);
      if (value) return value;
    } catch (e) {
      
    }
    
    return this.memoryStorage[key] || null;
  }

  _safeStorageSet(key, value) {
    const storedInCookie = this._setCookie(key, value);
    
    try {
      localStorage.setItem(key, value);
    } catch (e) {
      
    }
    
    try {
      sessionStorage.setItem(key, value);
    } catch (e) {
      
    }
    
    this.memoryStorage[key] = value;
    return storedInCookie;
  }

  _safeStorageRemove(key) {
    this._deleteCookie(key);
    
    try {
      localStorage.removeItem(key);
    } catch (e) {
      
    }
    
    try {
      sessionStorage.removeItem(key);
    } catch (e) {
      
    }
    
    delete this.memoryStorage[key];
  }

  
  getToken() {
    return this._safeStorageGet(this.tokenKey);
  }

  setToken(token) {
    this._safeStorageSet(this.tokenKey, token);
  }

  removeToken() {
    this._safeStorageRemove(this.tokenKey);
    this._safeStorageRemove(this.userKey);
    delete this.memoryStorage[this.tokenKey];
    delete this.memoryStorage[this.userKey];
  }

  getUser() {
    try {
      const userStr = this._safeStorageGet(this.userKey);
      return userStr ? JSON.parse(userStr) : null;
    } catch {
      return null;
    }
  }

  setUser(user) {
    this._safeStorageSet(this.userKey, JSON.stringify(user));
  }

  isLoggedIn() {
    return !!this.getToken();
  }

  
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const token = this.getToken();

    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers,
      },
      ...options,
    };

    if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
      config.body = JSON.stringify(config.body);
    }

    if (config.body instanceof FormData) {
      delete config.headers['Content-Type'];
    }

    try {
      const response = await fetch(url, config);

      if (response.status === 401) {
        this.removeToken();
        window.location.hash = '#/login';
        throw new Error('认证已过期，请重新登录');
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || data.error || `请求失败 (${response.status})`);
      }

      return data;
    } catch (error) {
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new Error('网络连接失败，请检查网络');
      }
      throw error;
    }
  }

  
  get(endpoint, params = {}) {
    const query = new URLSearchParams(params).toString();
    const url = query ? `${endpoint}?${query}` : endpoint;
    return this.request(url);
  }

  post(endpoint, body = {}) {
    return this.request(endpoint, { method: 'POST', body });
  }

  put(endpoint, body = {}) {
    return this.request(endpoint, { method: 'PUT', body });
  }

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  upload(endpoint, formData) {
    return this.request(endpoint, { method: 'POST', body: formData });
  }

  
  login(username, password, role) {
    return this.post('/auth/login', { username, password, role });
  }

  logout() {
    return this.post('/auth/logout');
  }

  getProfile() {
    return this.get('/auth/profile');
  }

  updateProfile(data) {
    return this.put('/auth/profile', data);
  }

  changePassword(data) {
    return this.put('/auth/password', data);
  }

  
  getStudentDashboard() {
    return this.get('/student/dashboard');
  }

  getStudentCourses(params = {}) {
    return this.get('/student/courses', params);
  }

  getStudentCourseDetail(courseId) {
    return this.get(`/student/courses/${courseId}`);
  }

  getStudentAssignments(params = {}) {
    return this.get('/student/assignments', params);
  }

  submitAssignment(assignmentId, data) {
    return this.post(`/student/assignments/${assignmentId}/submit`, data);
  }

  getStudentExams(params = {}) {
    return this.get('/student/exams', params);
  }

  getStudentResources(params = {}) {
    return this.get('/student/resources', params);
  }

  markResourceProgress(resourceId, data) {
    return this.post(`/student/resources/${resourceId}/progress`, data);
  }

  getStudentSchedule() {
    return this.get('/student/schedule');
  }

  getStudentReminders() {
    return this.get('/student/reminders');
  }

  markReminderRead(reminderId) {
    return this.put(`/student/reminders/${reminderId}/read`);
  }

  submitLeaveRequest(data) {
    return this.post('/student/leave', data);
  }

  getStudentLeaveRequests() {
    return this.get('/student/leave');
  }

  getElectricityBill() {
    return this.get('/student/life/electricity');
  }

  
  getConversations() {
    return this.get('/chat/conversations');
  }

  getMessages(conversationId, params = {}) {
    return this.get(`/chat/conversations/${conversationId}/messages`, params);
  }

  sendMessage(conversationId, data) {
    return this.post(`/chat/conversations/${conversationId}/messages`, data);
  }

  createConversation(data) {
    return this.post('/chat/conversations', data);
  }

  
  getTeacherDashboard() {
    return this.get('/teacher/dashboard');
  }

  getTeacherCourses(params = {}) {
    return this.get('/teacher/courses', params);
  }

  getTeacherCourseDetail(courseId) {
    return this.get(`/teacher/courses/${courseId}`);
  }

  uploadCourseware(courseId, formData) {
    return this.upload(`/teacher/courses/${courseId}/courseware`, formData);
  }

  deleteCourseware(courseId, coursewareId) {
    return this.delete(`/teacher/courses/${courseId}/courseware/${coursewareId}`);
  }

  createAssignment(data) {
    return this.post('/teacher/assignments', data);
  }

  getTeacherAssignments(params = {}) {
    return this.get('/teacher/assignments', params);
  }

  getAssignmentSubmissions(assignmentId) {
    return this.get(`/teacher/assignments/${assignmentId}/submissions`);
  }

  gradeSubmission(assignmentId, studentId, data) {
    return this.post(`/teacher/assignments/${assignmentId}/submissions/${studentId}/grade`, data);
  }

  batchGrade(assignmentId, data) {
    return this.post(`/teacher/assignments/${assignmentId}/batch-grade`, data);
  }

  generateAttendanceCode(courseId) {
    return this.post(`/teacher/courses/${courseId}/attendance/code`);
  }

  getAttendanceStatus(courseId, sessionId) {
    return this.get(`/teacher/courses/${courseId}/attendance/${sessionId}`);
  }

  getAttendanceStats(courseId) {
    return this.get(`/teacher/courses/${courseId}/attendance/stats`);
  }

  getExamAnalysis(courseId, examId) {
    return this.get(`/teacher/courses/${courseId}/exams/${examId}/analysis`);
  }

  getTeacherExams(params = {}) {
    return this.get('/teacher/exams', params);
  }

  
  checkIn(code) {
    return this.post('/student/attendance/checkin', { code });
  }

  
  getCounselorDashboard() {
    return this.get('/counselor/dashboard');
  }

  getLeaveRequests(params = {}) {
    return this.get('/counselor/leave', params);
  }

  approveLeaveRequest(requestId, data) {
    return this.put(`/counselor/leave/${requestId}/approve`, data);
  }

  rejectLeaveRequest(requestId, data) {
    return this.put(`/counselor/leave/${requestId}/reject`, data);
  }

  getClassStudents(params = {}) {
    return this.get('/counselor/students', params);
  }

  getStudentGradeDetail(studentId) {
    return this.get(`/counselor/students/${studentId}/grades`);
  }

  getClassOverview() {
    return this.get('/counselor/class/overview');
  }

  getClassGradeDistribution() {
    return this.get('/counselor/class/grades/distribution');
  }

  
  getAdminDashboard() {
    return this.get('/admin/dashboard');
  }

  getUsers(params = {}) {
    return this.get('/admin/users', params);
  }

  createUser(data) {
    return this.post('/admin/users', data);
  }

  updateUser(userId, data) {
    return this.put(`/admin/users/${userId}`, data);
  }

  deleteUser(userId) {
    return this.delete(`/admin/users/${userId}`);
  }

  toggleUserStatus(userId) {
    return this.put(`/admin/users/${userId}/toggle-status`);
  }

  getSystemMetrics() {
    return this.get('/admin/system/metrics');
  }

  getBugReports(params = {}) {
    return this.get('/admin/bugs', params);
  }

  updateBugReport(bugId, data) {
    return this.put(`/admin/bugs/${bugId}`, data);
  }

  getSystemLogs(params = {}) {
    return this.get('/admin/system/logs', params);
  }

  
  aiStudentAnalysis(studentId, params = {}) {
    return this.post('/ai/analysis/student', { student_id: studentId, ...params });
  }

  aiResourceGeneration(params) {
    return this.post('/ai/resources/generate', params);
  }

  aiExamAnalysis(params) {
    return this.post('/ai/analysis/exam', params);
  }

  aiLearningPlan(params) {
    return this.post('/ai/learning-plan', params);
  }

  aiSuggestQuestions(params) {
    return this.post('/ai/suggest-questions', params);
  }

  aiTeachingSuggestions(params) {
    return this.post('/ai/teaching-suggestions', params);
  }

  getAiTaskStatus(taskId) {
    return this.get(`/ai/tasks/${taskId}`);
  }

  
  uploadFile(file, purpose = 'general') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('purpose', purpose);
    return this.upload('/files/upload', formData);
  }
}


const apiService = new ApiService();


const api = {
  auth: {
    login: (username, password) => apiService.post('/auth/login', { username, password }),
    register: (data) => apiService.post('/auth/register', data),
    logout: () => apiService.post('/auth/logout'),
    me: () => apiService.get('/auth/me'),
  },
  student: {
    getCourses: (params) => apiService.get('/student/courses', params),
    getAssignments: (courseId) => apiService.get(`/student/assignments/${courseId}`),
    submitAssignment: (data) => apiService.post('/student/submit-assignment', data),
    getExamResults: (studentId) => apiService.get(`/student/exam-results/${studentId}`),
    getResources: (courseId) => apiService.get(`/student/resources/${courseId}`),
    getSchedule: () => apiService.get('/student/schedule'),
    getLeaveRequests: () => apiService.get('/student/leave-requests'),
    submitLeaveRequest: (data) => apiService.post('/student/leave-request', data),
  },
  teacher: {
    getCourses: (params) => apiService.get('/teacher/courses', params),
    getSubmissions: (assignmentId) => apiService.get(`/teacher/submissions/${assignmentId}`),
    gradeSubmission: (data) => apiService.post(`/teacher/grade-submission/${data.submission_id}`, { score: data.score, feedback: data.feedback }),
    createAssignment: (data) => apiService.post('/teacher/create-assignment', data),
    getClassAnalysis: (courseId) => apiService.get(`/teacher/class-analysis/${courseId}`),
  },
  counselor: {
    getLeaveRequests: (status) => apiService.get('/counselor/leave-requests', { status }),
    approveLeave: (requestId, data) => apiService.post(`/counselor/approve-leave/${requestId}`, data),
    getStudentGrades: (class_name) => apiService.get(`/counselor/student-grades/${class_name}`),
  },
  admin: {
    getServerStatus: () => apiService.get('/admin/server-status'),
    getSystemStats: () => apiService.get('/admin/system-stats'),
    getBugReports: () => apiService.get('/admin/bug-reports'),
  },
  agents: {
    analyzeStudent: (data) => apiService.post('/api/agents/analyze-student', data),
    generateResources: (data) => apiService.post('/api/agents/generate-resources', data),
    examAnalysis: (examId) => apiService.post('/api/agents/exam-analysis-ai', { exam_id: examId }),
    generateLearningPlan: (data) => apiService.post('/api/agents/learning-plan', data),
    getTeachingSuggestions: (data) => apiService.post('/api/agents/teaching-suggestions', data),
  },
  chat: {
    sendMessage: (data) => apiService.post('/api/chat/send-message', data),
    getMessages: (userId) => apiService.get(`/api/chat/messages/${userId}`),
    getGroups: () => apiService.get('/api/chat/groups'),
  },
  
  getToken: () => apiService.getToken(),
  setToken: (token) => apiService.setToken(token),
  removeToken: () => apiService.removeToken(),
  getUser: () => apiService.getUser(),
  setUser: (user) => apiService.setUser(user),
  isLoggedIn: () => apiService.isLoggedIn(),
};
