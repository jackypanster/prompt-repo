# **产品需求文档 (PRD): 提示词分享平台 (极简MVP)**

## **1\. 引言**

### **1.1 项目背景与目标**

本项目旨在开发一个极简的“提示词分享平台”应用，作为个人博客的延伸。核心目标是让博主（即应用所有者）能够方便地发布和管理其日常高频使用的AI提示词，并供公众匿名浏览和使用。此MVP（最小可行产品）将采用本地化部署和极简技术栈，以验证核心功能并快速上线。

**核心目标:**

* **内容发布与管理:** 博主能便捷地创建、编辑、分类和标记提示词。  
* **内容展示与使用:** 公众用户可以匿名浏览、复制和点赞提示词。  
* **极简架构验证:** 验证FastAPI后端（按需启动写入，持续服务前端）+ 本地SQLite \+ 静态化前端（FastAPI托管）的极简架构可行性。

### **1.2 项目原则**

* **单机本地化:** 所有核心组件（后端、数据库、前端服务）部署在同一台本地服务器。  
* **极致精简:** 专注于核心功能，技术选型力求简单、轻量。  
* **快速迭代:** 快速实现MVP，后续根据需求迭代。  
* **成本效益:** 最大限度降低外部服务依赖和直接成本。

## **2\. 技术栈 (极简MVP)**

* **后端服务:** FastAPI (Python) 单一应用  
  * **24/7运行:** 同时提供管理功能和公开访问功能
  * **管理功能:** 通过认证保护的管理端点，用于内容创建和管理
  * **公开功能:** 使用FastAPI的StaticFiles和Jinja2模板引擎托管和渲染前端页面  
* **数据库:** 本地SQLite数据库 (单个数据库文件，由FastAPI应用统一读写)。  
* **前端页面:**  
  * **基础:** 静态HTML，由FastAPI \+ Jinja2服务器端渲染生成。  
  * **样式:** Tailwind CSS 9。  
  * **UI组件 (推荐):** Basecoat UI (提供Shadcn UI风格的HTML/Tailwind组件) 10。  
  * **轻量级交互 (可选):** Alpine.js (配合Basecoat UI或自定义简单交互) 10。  
* **Python环境管理:** uv 11。  
* **部署:** 单台本地服务器（用户自行管理）。  
* **域名与HTTPS:** 用户自行购买域名，并为本地服务器配置DDNS（如果IP动态）和HTTPS（例如使用Let's Encrypt）13。

## **3\. 用户与角色**

* **博主/管理员 (Admin):** 应用的唯一所有者和内容管理者。通过HTTP Basic Auth或API密钥访问管理端点（无需复杂Web登录界面）。  
* **普通用户/访客 (User/Visitor):** 匿名访问前端静态页面的公众用户。

## **4\. MVP核心功能需求**

### **4.1 后端管理功能 (FastAPI管理端点)**

* **FR1: 管理员认证 (简化)**  
  * **FR1.1:** 管理端点通过HTTP Basic Auth或API密钥进行保护。MVP阶段不实现复杂的Web登录界面。  
* **FR2: 提示词管理 (Markdown)**  
  * **FR2.1:** 管理员可以创建新的提示词，内容以Markdown格式输入，存储到本地SQLite数据库 24。  
  * **FR2.2:** 管理员可以查看、编辑和删除已发布的提示词。  
* **FR3: 提示词分类**  
  * **FR3.1:** 管理员在发布或编辑提示词时，可以为提示词选择一个分类。  
  * **FR3.2:** 分类信息与提示词一同存储在SQLite。  
* **FR4: 提示词标签**  
  * **FR4.1:** 管理员在发布或编辑提示词时，可以为提示词添加一个或多个标签。  
  * **FR4.2:** 标签信息与提示词通过多对多关系存储在SQLite。

### **4.2 前端展示功能 (FastAPI公开端点)**

* **FR5: 提示词浏览**  
  * **FR5.1:** 任何用户都可以匿名访问由FastAPI + Jinja2动态生成的HTML页面，浏览提示词列表。  
  * **FR5.2:** 提示词列表数据从本地SQLite数据库读取并渲染到Jinja2模板中。  
  * **FR5.3:** Markdown内容在服务器端渲染为HTML（通过Python Markdown库集成到Jinja2流程中）。  
* **FR6: 按分类/标签筛选**  
  * **FR6.1:** 用户可以通过URL参数或页面链接筛选特定分类或标签下的提示词。FastAPI后端处理筛选逻辑并渲染相应页面。  
* **FR7: 提示词详情查看**  
  * **FR7.1:** 用户可以访问单个提示词的详情页面。  
* **FR8: 提示词复制**  
  * **FR8.1:** 用户可以通过前端交互（例如，一个复制按钮，可能由Alpine.js驱动）复制提示词的Markdown原文。  
  * **FR8.2:** 每次复制操作会触发一个轻量级的后端API调用，使对应提示词在SQLite中的copy\_count原子性地增加1。此API端点需防范滥用（例如，基于IP的简单速率限制）。  
* **FR9: 提示词点赞**  
  * **FR9.1:** 用户可以对提示词进行点赞。  
  * **FR9.2:** 每个用户（通过IP地址或浏览器指纹等方式进行简单识别，MVP阶段不追求完美防刷）对同一提示词只能点赞一次。点赞状态可存储在浏览器localStorage或通过后端API（同样需要简单防滥用）记录到SQLite。  
  * **FR9.3:** 点赞数据（例如，一个likes表关联到prompts表，或直接在prompts表增加like\_count）写入SQLite。  
* **FR10: 热门排序**  
  * **FR10.1:** 提示词列表可以按复制数量 (copy\_count) 或点赞数量进行热门排序。

## **5\. 非功能性需求 (MVP)**

* **NFR1: 本地化部署:** 整个应用（FastAPI服务、SQLite数据库）部署在单台本地服务器上。  
* **NFR2: 响应式设计:** 前端HTML页面应能良好适应桌面和主流手机浏览器。  
* **NFR3: 安全性:**  
  * **NFR3.1:** 本地服务器需进行基础安全加固（防火墙、SSH安全、定期更新）。  
  * **NFR3.2:** FastAPI管理端API需通过简单有效的方式进行认证（如API密钥或HTTP Basic Auth）。  
  * **NFR3.3:** SQLite数据库文件需配置严格的文件系统权限 27。  
  * **NFR3.4:** 前端公开访问的写入操作（点赞、复制计数）需有基础的防滥用机制。  
  * **NFR3.5:** 强制HTTPS。  
* **NFR4: 轻量级:** 应用资源占用低，SQLite启用WAL模式以优化并发读写 30。  
* **NFR5: 日志记录:** FastAPI应用应记录关键操作和错误日志，方便追踪和定位问题。

## **6\. 未来考虑 (MVP后)**

* **FR\_Future1: 用户评论系统。**  
* **FR\_Future2: 博主打赏功能。**  
* **NFR\_Future1: 更完善的内容审核机制。**  
* **NFR\_Future2: 更高级的搜索功能。**  
* **NFR\_Future3: 迁移到云托管方案（如果流量增长或运维需求增加）。**

## **7\. 名词解释**

* **提示词 (Prompt):** 用于与AI模型交互的文本输入。  
* **MVP (Minimum Viable Product):** 最小可行产品。  
* **FastAPI:** Python Web框架。  
* **SQLite:** 轻量级文件型数据库。  
* **Jinja2:** Python模板引擎。  
* **Tailwind CSS:** 原子化CSS框架。  
* **Basecoat UI:** 提供Shadcn UI风格的HTML/Tailwind组件库。  
* **Alpine.js:** 轻量级JavaScript框架。  
* **uv:** Python包管理工具。  
* **DDNS (Dynamic DNS):** 动态域名解析服务。  
* **WAL (Write-Ahead Logging):** SQLite的一种日志模式，改善并发性能。

#### **引用的著作**

1. Fast API for Web Development: 2025 Detailed Review \- Aloa, 访问时间为 六月 1, 2025， [https://aloa.co/blog/fast-api](https://aloa.co/blog/fast-api)  
2. FastAPI: The Modern Python Framework For Web Developers \- BSuperior, 访问时间为 六月 1, 2025， [https://bsuperiorsystem.com/blog/fastapi-the-modern-python-framework/](https://bsuperiorsystem.com/blog/fastapi-the-modern-python-framework/)  
3. Understanding and Implementing Static Files in Fast API \- Orchestra, 访问时间为 六月 2, 2025， [https://www.getorchestra.io/guides/understanding-and-implementing-static-files-in-fast-api](https://www.getorchestra.io/guides/understanding-and-implementing-static-files-in-fast-api)  
4. Static Files \- StaticFiles \- FastAPI, 访问时间为 六月 2, 2025， [https://fastapi.tiangolo.com/reference/staticfiles/](https://fastapi.tiangolo.com/reference/staticfiles/)  
5. Show HN: Basecoat – All of the shadcn/ui magic, none of the React ..., 访问时间为 六月 2, 2025， [https://news.ycombinator.com/item?id=43925566](https://news.ycombinator.com/item?id=43925566)  
6. Using uv with FastAPI | uv \- Astral Docs, 访问时间为 六月 1, 2025， [https://docs.astral.sh/uv/guides/integration/fastapi/](https://docs.astral.sh/uv/guides/integration/fastapi/)  
7. Next.js FastAPI Template: how to build and deploy scalable apps \- Vinta Software, 访问时间为 六月 2, 2025， [https://www.vintasoftware.com/blog/next-js-fastapi-template](https://www.vintasoftware.com/blog/next-js-fastapi-template)  
8. Logging | Supabase Docs, 访问时间为 六月 1, 2025， [https://supabase.com/docs/guides/telemetry/logs](https://supabase.com/docs/guides/telemetry/logs)  
9. Running fastapi app using uvicorn on ubuntu server \- Stack Overflow, 访问时间为 六月 2, 2025， [https://stackoverflow.com/questions/62898917/running-fastapi-app-using-uvicorn-on-ubuntu-server](https://stackoverflow.com/questions/62898917/running-fastapi-app-using-uvicorn-on-ubuntu-server)  
10. hunvreus/basecoat: A components library built with ... \- GitHub, 访问时间为 六月 2, 2025， [https://github.com/hunvreus/basecoat](https://github.com/hunvreus/basecoat)  
11. Python UV: The Ultimate Guide to the Fastest Python Package Manager \- DataCamp, 访问时间为 六月 1, 2025， [https://www.datacamp.com/tutorial/python-uv](https://www.datacamp.com/tutorial/python-uv)  
12. Managing Python Projects With uv: An All-in-One Solution \- Real Python, 访问时间为 六月 1, 2025， [https://realpython.com/python-uv/](https://realpython.com/python-uv/)  
13. Finished building my app (Next.js \+ Supabase). Is Vercel too expensive for long-term production? What are better hosting options for EU-based apps? : r/nextjs \- Reddit, 访问时间为 六月 1, 2025， [https://www.reddit.com/r/nextjs/comments/1krst41/finished\_building\_my\_app\_nextjs\_supabase\_is/](https://www.reddit.com/r/nextjs/comments/1krst41/finished_building_my_app_nextjs_supabase_is/)  
14. RLS diving me crazy : r/Supabase \- Reddit, 访问时间为 六月 1, 2025， [https://www.reddit.com/r/Supabase/comments/1g4vi15/rls\_diving\_me\_crazy/](https://www.reddit.com/r/Supabase/comments/1g4vi15/rls_diving_me_crazy/)  
15. PostgREST Aggregate Functions \- Supabase, 访问时间为 六月 1, 2025， [https://supabase.com/blog/postgrest-aggregate-functions](https://supabase.com/blog/postgrest-aggregate-functions)  
16. Security \- FastAPI, 访问时间为 六月 1, 2025， [https://fastapi.tiangolo.com/tutorial/security/](https://fastapi.tiangolo.com/tutorial/security/)  
17. DDNS: Self-Hosting For Businesses Without Static IPs, 访问时间为 六月 2, 2025， [https://www.businessbroadbandhub.co.uk/blog/dynamic-dns/](https://www.businessbroadbandhub.co.uk/blog/dynamic-dns/)  
18. Setting Up Dynamic DNS on a Raspberry Pi for Self-Hosting \- Kev's Robots, 访问时间为 六月 2, 2025， [https://www.kevsrobots.com/blog/dynamic-dns.html](https://www.kevsrobots.com/blog/dynamic-dns.html)  
19. Secure Your Localhost with Let's Encrypt: A Step-by-Step Guide, 访问时间为 六月 2, 2025， [https://locall.host/letsencrypt-localhost/](https://locall.host/letsencrypt-localhost/)  
20. Vite \- Shadcn UI, 访问时间为 六月 2, 2025， [https://ui.shadcn.com/docs/installation/vite](https://ui.shadcn.com/docs/installation/vite)  
21. How to ensure data consistency in system with multiple databases?, 访问时间为 六月 1, 2025， [https://softwareengineering.stackexchange.com/questions/447680/how-to-ensure-data-consistency-in-system-with-multiple-databases](https://softwareengineering.stackexchange.com/questions/447680/how-to-ensure-data-consistency-in-system-with-multiple-databases)  
22. FastAPI and HTTP Basic Authentication: A Detailed Tutorial \- Orchestra, 访问时间为 六月 2, 2025， [https://www.getorchestra.io/guides/fastapi-and-http-basic-authentication-a-detailed-tutorial](https://www.getorchestra.io/guides/fastapi-and-http-basic-authentication-a-detailed-tutorial)  
23. HTTP Basic Auth \- FastAPI, 访问时间为 六月 2, 2025， [https://fastapi.tiangolo.com/advanced/security/http-basic-auth/](https://fastapi.tiangolo.com/advanced/security/http-basic-auth/)  
24. Pages Router: Render Markdown | Next.js, 访问时间为 六月 1, 2025， [https://nextjs.org/learn/pages-router/dynamic-routes-render-markdown](https://nextjs.org/learn/pages-router/dynamic-routes-render-markdown)  
25. Guides: MDX \- Next.js, 访问时间为 六月 1, 2025， [https://nextjs.org/docs/app/guides/mdx](https://nextjs.org/docs/app/guides/mdx)  
26. remarkjs/react-markdown: Markdown component for React \- GitHub, 访问时间为 六月 1, 2025， [https://github.com/remarkjs/react-markdown](https://github.com/remarkjs/react-markdown)  
27. Basic Security Practices for SQLite: Safeguarding Your Data \- DEV ..., 访问时间为 六月 1, 2025， [https://dev.to/stephenc222/basic-security-practices-for-sqlite-safeguarding-your-data-23lh](https://dev.to/stephenc222/basic-security-practices-for-sqlite-safeguarding-your-data-23lh)  
28. Basic Security Practices for SQLite: Safeguarding Your Data, 访问时间为 六月 2, 2025， [https://stephencollins.tech/posts/basic-security-practices-sqlite](https://stephencollins.tech/posts/basic-security-practices-sqlite)  
29. How to deploy a next.js app with local mongodb or sqlite / mysql without using a cloud provider? : r/nextjs \- Reddit, 访问时间为 六月 1, 2025， [https://www.reddit.com/r/nextjs/comments/gvwek8/how\_to\_deploy\_a\_nextjs\_app\_with\_local\_mongodb\_or/](https://www.reddit.com/r/nextjs/comments/gvwek8/how_to_deploy_a_nextjs_app_with_local_mongodb_or/)  
30. What is shadcn-ui? A Deep Dive into the Modern UI Library \- Apidog, 访问时间为 六月 1, 2025， [https://apidog.com/blog/what-is-shadcn-ui/](https://apidog.com/blog/what-is-shadcn-ui/)  
31. supabase RLS with clerk \#33091 \- GitHub, 访问时间为 六月 1, 2025， [https://github.com/orgs/supabase/discussions/33091](https://github.com/orgs/supabase/discussions/33091)  
32. Auth Hooks | Supabase Docs \- Vercel, 访问时间为 六月 1, 2025， [https://docs-4ta3lngqn-supabase.vercel.app/docs/guides/auth/auth-hooks](https://docs-4ta3lngqn-supabase.vercel.app/docs/guides/auth/auth-hooks)  
33. Begin Concurrent \- SQLite, 访问时间为 六月 2, 2025， [https://www.sqlite.org/src/doc/begin-concurrent/doc/begin\_concurrent.md](https://www.sqlite.org/src/doc/begin-concurrent/doc/begin_concurrent.md)  
34. Abusing SQLite to Handle Concurrency \- SkyPilot Blog, 访问时间为 六月 2, 2025， [https://blog.skypilot.co/abusing-sqlite-to-handle-concurrency/](https://blog.skypilot.co/abusing-sqlite-to-handle-concurrency/)  
35. How to backup sqlite database? \- Stack Overflow, 访问时间为 六月 2, 2025， [https://stackoverflow.com/questions/25675314/how-to-backup-sqlite-database](https://stackoverflow.com/questions/25675314/how-to-backup-sqlite-database)  
36. Write-Ahead Logging \- SQLite, 访问时间为 六月 2, 2025， [https://sqlite.org/wal.html](https://sqlite.org/wal.html)  
37. DuckDB vs SQLite: Choosing the Right Embedded Database | Better Stack Community, 访问时间为 六月 2, 2025， [https://betterstack.com/community/guides/scaling-python/duckdb-vs-sqlite/](https://betterstack.com/community/guides/scaling-python/duckdb-vs-sqlite/)