# Wegatsaucee Fashion Hub - Professional E-commerce Platform

A modern Flask e-commerce website for fashion retail with international payment support and package tracking.

## 🚀 Features

### Customer Features
- **Modern UI/UX** - Responsive design with smooth animations
- **Product Catalog** - Advanced filtering, search, and sorting
- **Shopping Cart** - Persistent cart with size/color selection
- **International Payments** - Stripe & PayPal integration
- **Package Tracking** - Real-time order tracking system
- **User Accounts** - Registration, login, profile management
- **Reviews & Ratings** - Customer feedback system
- **Wishlist** - Save favorite products

### Admin Features
- **Product Management** - Add, edit, delete products
- **Order Management** - Process and track orders
- **User Management** - Customer account oversight
- **Analytics Dashboard** - Sales and performance metrics

### Technical Features
- **Security** - JWT authentication, rate limiting, input validation
- **Performance** - Optimized queries, image compression
- **Scalability** - Modular architecture, cloud-ready
- **SEO Optimized** - Meta tags, structured data

## 🛠️ Tech Stack

- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Database (development)
- **Jinja2** - Template engine
- **Tailwind CSS** - Styling (CDN)
- **M-Pesa & Flutterwave** - Payment processing

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup Steps

1. **Install Dependencies**
   ```bash
   cd turktrendyshop
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   - Edit `.env` file with your credentials
   - Admin login: username=`admin`, password=`admin123`

3. **Run Application**
   ```bash
   python app.py
   ```

4. **Access Application**
   - Homepage: http://127.0.0.1:5000/
   - Admin Panel: http://127.0.0.1:5000/admin/login

## 🌐 Deployment

### PythonAnywhere (Recommended)

**Quick Fix for Current Deployment Issues:**

If you're seeing database errors, run this one command:

```bash
cd ~/wegatsauceefashionhub && source ~/.virtualenvs/myenv/bin/activate && python quick_fix.py
```

Then reload your web app in the PythonAnywhere dashboard.

**Fresh Deployment:**

1. Upload project files to PythonAnywhere
2. Create virtual environment:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 myenv
   pip install -r requirements.txt
   ```
3. Create `.env` file with:
   ```
   SECRET_KEY=your-secret-key
   ADMIN_USER=admin
   ADMIN_PASS=admin123
   ```
4. Run setup:
   ```bash
   python quick_fix.py
   ```
5. Configure WSGI file (see `PYTHONANYWHERE_FIX.md`)
6. Reload web app

**Other Platforms:**
- **Heroku**: Free tier with SQLite
- **AWS EC2**: Full control VPS
- **DigitalOcean**: Cost-effective droplets

## 📱 Key Routes

- `/` - Homepage
- `/products` - Product catalog
- `/cart` - Shopping cart
- `/admin/login` - Admin panel (admin/admin123)
- `/register` - User registration
- `/login` - User login



## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Email: support@wegatsaucee.com
- Documentation: [Wiki](link-to-wiki)

## 🚀 Roadmap

### Phase 1 (Current)
- ✅ Basic e-commerce functionality
- ✅ Payment integration
- ✅ Order tracking

### Phase 2 (Next)
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Social media integration

### Phase 3 (Future)
- [ ] AI-powered recommendations
- [ ] Augmented reality try-on
- [ ] Subscription boxes
- [ ] Marketplace for multiple vendors

---

**Built with ❤️ for modern fashion retail**