# 1. استرجاع أحدث المراجع من remote repository
git fetch origin

# 2. تحديث local development branch
git checkout development
git pull origin development

# 3. الانتقال إلى الفرع الشخصي الخاص بك
git checkout <username>

# 4. البرمجة وatomic commits
(git add . && git commit -m "FEATURE(#123): وصف مختصر")

# 5. قبل الرفع، مزامنة فرعك مع development
git fetch origin                       # (اختياري إذا قمت بالفعل بتنفيذ fetch)
git rebase origin/development

# 6. رفع commits على فرعك الشخصي
git push                               # (أو `git push -u origin <username>` في المرة الأولى فقط)
# 7. إنشاء Pull Request إلى "development"
1. على GitHub.  
2. اذهب إلى ال**tab** **Pull requests**.  
3. اضغط على **New pull request**.  
4. حدد:  
   - **Base branch**: `development`  
   - **Compare branch**: `<username>`  
5. اكتب عنوان ووصفًا واضحًا.  
6. اضغط **Create pull request**.  
