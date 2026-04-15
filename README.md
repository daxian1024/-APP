部署docker环境：
cd deploy
docker compose up -d


3) 初始化数据库
进入 backend 目录执行：

python seed.py
4) 启动后端
仍在 backend 目录：
cd backend
python run.py
成功后访问：


http://127.0.0.1:5000/ 现在直接打开项目首页（frontend/index.html）
http://127.0.0.1:5000/admin 打开管理端（frontend/admin.html）


. 开发联调模式（推荐）
启后端（项目根）：
cd backend
python run.py
启前端（新开终端）：
cd frontend-vue
npm run dev
打开：
前端开发页：http://127.0.0.1:5173
后端接口：http://127.0.0.1:5000/api/...
B. 一体化运行模式（发布模拟）
先打包前端：
cd frontend-vue
npm run build
再启动后端：
cd ../backend
python run.py
打开：
http://127.0.0.1:5000/（就是最新 Vue 页面，不再是旧 html）


推送git:
git add .
git commit -m "更新内容"
git push