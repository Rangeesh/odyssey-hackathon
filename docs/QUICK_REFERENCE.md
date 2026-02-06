# LYRA - Quick Reference Card

## 🚀 Getting Started

```bash
cd backend
./start_server.sh
```
Open: **http://localhost:8000**

## 🎵 Generate a Video

1. Start typing: `Song Name`
2. Click: **🔍 Find Lyrics**
3. Review lyrics
4. Click: **🎬 Generate Video**
5. Watch: Images appear in real-time
6. Enjoy: Final video plays automatically

## 🌙 Toggle Dark Mode

Click the button in top-right corner:
- 🌙 = Click to enable dark mode
- ☀️ = Click to enable light mode

## ❌ Cancel a Job

1. Find job with "Pending" or "Processing" status
2. Click: **❌ Cancel** button
3. Confirm: Click OK in dialog

## 📊 Job Statuses

| Status | Meaning | Can Cancel? |
|--------|---------|-------------|
| Pending | Waiting to start | ✅ Yes |
| Processing | Currently running | ✅ Yes |
| Completed | Finished successfully | ❌ No |
| Failed | Error occurred | ❌ No |
| Cancelled | Stopped by user | ❌ No |

## 🎨 Themes

### Light Mode (Default)
- Purple gradient background
- White cards
- Dark text
- Best for: Daytime, bright rooms

### Dark Mode
- Dark blue gradient background
- Deep blue cards
- Light text
- Best for: Nighttime, dark rooms

## ⌨️ Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Focus search | Tab |
| Submit form | Enter |
| Toggle theme | Tab to button, Enter |
| Refresh page | F5 or Ctrl+R |

## 🔧 Troubleshooting

### "Lyrics not found"
- Check song name spelling
- Try a more popular song
- Include artist name

### Server won't start
```bash
lsof -ti:8000 | xargs kill -9
cd backend && ./start_server.sh
```

### Theme not saving
- Enable browser cookies
- Clear cache and reload
- Check JavaScript is enabled

## 📁 File Locations

| Item | Path |
|------|------|
| Server script | `backend/start_server.sh` |
| Database | `backend/db.sqlite3` |
| Videos | `backend/media/generated_content/` |
| Logs | Terminal output |

## 🌐 URLs

| Page | URL |
|------|-----|
| Main app | http://localhost:8000 |
| Admin | http://localhost:8000/admin/ |
| API jobs | http://localhost:8000/api/jobs/ |

## 💡 Tips

1. **Popular songs work best** - Better lyrics coverage
2. **Cancel early** - Save API credits if wrong song
3. **Use dark mode at night** - Reduces eye strain
4. **Wait patiently** - Video generation takes time
5. **Check progress** - Auto-refreshes every 3 seconds

## 🎯 Example Songs

Try these for best results:
- `Bohemian Rhapsody Queen`
- `Imagine John Lennon`
- `Hotel California Eagles`
- `Shape of You Ed Sheeran`
- `Billie Jean Michael Jackson`

## 🔑 Environment Variables

Required in `.env` file:
```bash
GOOGLE_API_KEY=your_gemini_key
ODYSSEY_API_KEY=your_odyssey_key
```

## 📞 Quick Commands

### Start Server
```bash
cd backend && ./start_server.sh
```

### Stop Server
```
Ctrl+C in terminal
```

### Kill Port 8000
```bash
lsof -ti:8000 | xargs kill -9
```

### Reset Database
```bash
cd backend
rm db.sqlite3
python manage.py migrate
```

### View Logs
Check terminal where server is running

## 🎨 Color Codes

### Light Mode
- Background: `#667eea` → `#764ba2`
- Cards: `#ffffff`
- Text: `#333333`
- Accent: `#667eea`

### Dark Mode
- Background: `#1a1a2e` → `#16213e`
- Cards: `#0f3460`
- Text: `#e0e0e0`
- Accent: `#7b68ee`

## 📚 Documentation

| Topic | File |
|-------|------|
| Setup | README.md |
| Usage | USAGE_GUIDE.md |
| Running | RUNNING.md |
| Dark Mode | DARK_MODE.md |
| Cancellation | CANCEL_FEATURE.md |
| Features | FEATURES_SUMMARY.md |
| Changes | CHANGELOG.md |

## ⚡ Performance

| Metric | Value |
|--------|-------|
| Video generation | 5-10 min |
| Page load | < 1 sec |
| Auto-refresh | 3 sec |
| Theme switch | Instant |

## 🔒 Security

- No authentication required (local dev)
- CSRF protection enabled
- CORS restricted to localhost
- UUID-based job IDs

## 🎓 Learning Path

1. **Day 1**: Generate your first video
2. **Day 2**: Try dark mode
3. **Day 3**: Cancel a job
4. **Day 4**: Explore different songs
5. **Day 5**: Customize themes (advanced)

---

**Need more help?** Check the full documentation files! 📖
