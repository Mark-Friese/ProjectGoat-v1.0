# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in ProjectGoat, please report it by:

1. **Do NOT** open a public GitHub issue
2. Email the maintainers directly (or create a private security advisory on GitHub)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if you have one)

We will respond within 48 hours and work with you to address the issue.

## Security Features

### Authentication
- Bcrypt password hashing (no plaintext passwords)
- Session-based authentication with timeouts
  - 30-minute idle timeout
  - 8-hour absolute timeout
- CSRF protection on all state-changing operations
- Rate limiting on login attempts (5 attempts per 15 minutes)

### Network Security
- Localhost-only binding by default (127.0.0.1)
- CORS restricted to configured origins
- Security headers in production:
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Strict-Transport-Security (HTTPS only)

### Data Protection
- SQL injection prevention (SQLAlchemy ORM)
- Input validation via Pydantic schemas
- Session secrets should be changed in production

### Database
- Local deployment: SQLite (file-based, no network exposure)
- Production deployment: PostgreSQL with managed hosting

## Best Practices for Deployment

### Local Deployment
- Uses localhost-only binding (not exposed to network)
- No additional security measures needed for personal use
- Keep your laptop updated and secure

### Online Production Deployment

**Required:**
1. **HTTPS Only**: Never deploy without SSL/TLS
2. **Strong Session Secret**: Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
3. **Environment Variables**: Never commit `.env` files
4. **Database Credentials**: Use platform-managed secrets
5. **CORS Configuration**: Restrict to your domain only

**Recommended:**
1. Regular backups of database
2. Monitor error logs for suspicious activity
3. Keep dependencies updated
4. Enable platform security features (Render/Railway provide these)
5. Review audit logs periodically

## Known Limitations

### Local Deployment
- **Not suitable for network deployment**: Designed for localhost use
- **Single user**: SQLite not optimized for concurrent access
- **No HTTPS**: Local deployment uses HTTP (acceptable for localhost)

### Production Deployment
- **Requires PostgreSQL**: SQLite not suitable for multi-user scenarios
- **Platform security**: Relies on hosting platform (Railway/Render/etc.) for:
  - DDoS protection
  - SSL certificate management
  - Network-level security

## Security Checklist

Before deploying to production:

- [ ] Changed `SESSION_SECRET` from default
- [ ] Set `ENVIRONMENT=production`
- [ ] Using PostgreSQL (not SQLite)
- [ ] HTTPS enabled (automatic on Railway/Render)
- [ ] `PRODUCTION_ORIGIN` set to your domain
- [ ] No `.env` files committed to git
- [ ] Database backups configured
- [ ] Error monitoring enabled (optional but recommended)
- [ ] Reviewed all environment variables
- [ ] Tested authentication flows
- [ ] Verified CORS settings

## Dependency Security

Dependencies are regularly updated. To check for known vulnerabilities:

```bash
# Python dependencies
pip install safety
safety check -r requirements.txt

# JavaScript dependencies
npm audit
```

## Responsible Disclosure

We appreciate responsible disclosure of security issues. Contributors who report valid security vulnerabilities will be acknowledged in release notes (with permission).
