     STDIN
   1 """
   2 CRUD operations for authentication and authorization (Async version)
   3 """
   4 from sqlalchemy.ext.asyncio import AsyncSession
   5 from sqlalchemy import and_, or_, select, update, func
   6 from datetime import datetime, timedelta
   7 from typing import Optional, List
   8 from uuid import UUID
   9 
  10 from app.models_auth import User, RefreshToken, AuditLog, Team
  11 from app.auth_utils import hash_password, verify_password, hash_token
  12 from app.permissions import can_manage_user
  13 
  14 
  15 # User operations
  16 
  17 async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
  18     """Get user by ID."""
  19     result = await db.execute(select(User).filter(User.id == user_id))
  20     return result.scalar_one_or_none()
  21 
  22 
  23 async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
  24     """Get user by username."""
  25     result = await db.execute(select(User).filter(User.username == username))
  26     return result.scalar_one_or_none()
  27 
  28 
  29 async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
  30     """Get user by email."""
  31     result = await db.execute(select(User).filter(User.email == email))
  32     return result.scalar_one_or_none()
  33 
  34 
  35 async def create_user(
  36     db: AsyncSession,
  37     username: str,
  38     email: str,
  39     password: str,
  40     role: str,
  41     full_name: Optional[str] = None,
  42     manager_id: Optional[UUID] = None,
  43     team_id: Optional[UUID] = None,
  44     created_by_id: Optional[UUID] = None,
  45 ) -> User:
  46     """Create a new user."""
  47     user = User(
  48         username=username,
  49         email=email,
  50         password_hash=hash_password(password),
  51         role=role,
  52         full_name=full_name,
  53         manager_id=manager_id,
  54         team_id=team_id,
  55         created_by_id=created_by_id,
  56         is_active=True,
  57         must_change_password=True,
  58     )
  59     db.add(user)
  60     await db.flush()
  61     await db.refresh(user)
  62     return user
  63 
  64 
  65 async def update_user(
  66     db: AsyncSession,
  67     user_id: UUID,
  68     email: Optional[str] = None,
  69     full_name: Optional[str] = None,
  70     role: Optional[str] = None,
  71     manager_id: Optional[UUID] = None,
  72     team_id: Optional[UUID] = None,
  73     is_active: Optional[bool] = None,
  74 ) -> Optional[User]:
  75     """Update user information."""
  76     user = await get_user_by_id(db, user_id)
  77     if not user:
  78         return None
  79     
  80     if email is not None:
  81         user.email = email
  82     if full_name is not None:
  83         user.full_name = full_name
  84     if role is not None:
  85         user.role = role
  86     if manager_id is not None:
  87         user.manager_id = manager_id
  88     if team_id is not None:
  89         user.team_id = team_id
  90     if is_active is not None:
  91         user.is_active = is_active
  92     
  93     user.updated_at = datetime.utcnow()
  94     await db.flush()
  95     await db.refresh(user)
  96     return user
  97 
  98 
  99 async def change_password(
 100     db: AsyncSession,
 101     user_id: UUID,
 102     old_password: str,
 103     new_password: str,
 104 ) -> bool:
 105     """Change user password."""
 106     user = await get_user_by_id(db, user_id)
 107     if not user:
 108         return False
 109     
 110     if not verify_password(old_password, user.password_hash):
 111         return False
 112     
 113     user.password_hash = hash_password(new_password)
 114     user.must_change_password = False
 115     user.updated_at = datetime.utcnow()
 116     await db.flush()
 117     return True
 118 
 119 
 120 async def reset_password(db: AsyncSession, user_id: UUID, new_password: str) -> bool:
 121     """Reset user password (admin action)."""
 122     user = await get_user_by_id(db, user_id)
 123     if not user:
 124         return False
 125     
 126     user.password_hash = hash_password(new_password)
 127     user.must_change_password = True
 128     user.updated_at = datetime.utcnow()
 129     await db.flush()
 130     return True
 131 
 132 
 133 async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
 134     """Authenticate a user with username and password."""
 135     user = await get_user_by_username(db, username)
 136     if not user:
 137         return None
 138     if not user.is_active:
 139         return None
 140     if not verify_password(password, user.password_hash):
 141         return None
 142     
 143     # Update last login
 144     user.last_login = datetime.utcnow()
 145     await db.flush()
 146     await db.refresh(user)
 147     
 148     return user
 149 
 150 
 151 async def list_users(
 152     db: AsyncSession,
 153     skip: int = 0,
 154     limit: int = 100,
 155     role: Optional[str] = None,
 156     is_active: Optional[bool] = None,
 157     manager_id: Optional[UUID] = None,
 158 ) -> tuple[List[User], int]:
 159     """List users with filtering and pagination."""
 160     query = select(User)
 161     
 162     if role:
 163         query = query.filter(User.role == role)
 164     if is_active is not None:
 165         query = query.filter(User.is_active == is_active)
 166     if manager_id:
 167         query = query.filter(User.manager_id == manager_id)
 168     
 169     # Get total count
 170     count_query = select(func.count()).select_from(query.subquery())
 171     total_result = await db.execute(count_query)
 172     total = total_result.scalar()
 173     
 174     # Get paginated results
 175     query = query.offset(skip).limit(limit)
 176     result = await db.execute(query)
 177     users = result.scalars().all()
 178     
 179     return list(users), total
 180 
 181 
 182 async def deactivate_user(db: AsyncSession, user_id: UUID) -> bool:
 183     """Deactivate a user account."""
 184     user = await get_user_by_id(db, user_id)
 185     if not user:
 186         return False
 187     
 188     user.is_active = False
 189     user.updated_at = datetime.utcnow()
 190     await db.flush()
 191     return True
 192 
 193 
 194 async def activate_user(db: AsyncSession, user_id: UUID) -> bool:
 195     """Activate a user account."""
 196     user = await get_user_by_id(db, user_id)
 197     if not user:
 198         return False
 199     
 200     user.is_active = True
 201     user.updated_at = datetime.utcnow()
 202     await db.flush()
 203     return True
 204 
 205 
 206 # Refresh token operations
 207 
 208 async def create_refresh_token(
 209     db: AsyncSession,
 210     user_id: UUID,
 211     token: str,
 212     expires_at: datetime,
 213 ) -> RefreshToken:
 214     """Create a refresh token."""
 215     refresh_token = RefreshToken(
 216         user_id=user_id,
 217         token_hash=hash_token(token),
 218         expires_at=expires_at,
 219     )
 220     db.add(refresh_token)
 221     await db.flush()
 222     await db.refresh(refresh_token)
 223     return refresh_token
 224 
 225 
 226 async def get_refresh_token(db: AsyncSession, token: str) -> Optional[RefreshToken]:
 227     """Get refresh token by token value."""
 228     token_hash = hash_token(token)
 229     result = await db.execute(
 230         select(RefreshToken).filter(
 231             and_(
 232                 RefreshToken.token_hash == token_hash,
 233                 RefreshToken.revoked_at.is_(None),
 234                 RefreshToken.expires_at > datetime.utcnow(),
 235             )
 236         )
 237     )
 238     return result.scalar_one_or_none()
 239 
 240 
 241 async def revoke_refresh_token(db: AsyncSession, token: str) -> bool:
 242     """Revoke a refresh token."""
 243     token_hash = hash_token(token)
 244     result = await db.execute(
 245         select(RefreshToken).filter(RefreshToken.token_hash == token_hash)
 246     )
 247     refresh_token = result.scalar_one_or_none()
 248     
 249     if not refresh_token:
 250         return False
 251     
 252     refresh_token.revoked_at = datetime.utcnow()
 253     await db.flush()
 254     return True
 255 
 256 
 257 async def revoke_all_user_tokens(db: AsyncSession, user_id: UUID) -> int:
 258     """Revoke all refresh tokens for a user."""
 259     stmt = (
 260         update(RefreshToken)
 261         .where(
 262             and_(
 263                 RefreshToken.user_id == user_id,
 264                 RefreshToken.revoked_at.is_(None),
 265             )
 266         )
 267         .values(revoked_at=datetime.utcnow())
 268     )
 269     result = await db.execute(stmt)
 270     await db.flush()
 271     return result.rowcount
 272 
 273 
 274 # Audit log operations
 275 
 276 async def create_audit_log(
 277     db: AsyncSession,
 278     user_id: Optional[UUID],
 279     action: str,
 280     resource_type: Optional[str] = None,
 281     resource_id: Optional[UUID] = None,
 282     details: Optional[dict] = None,
 283     ip_address: Optional[str] = None,
 284     user_agent: Optional[str] = None,
 285 ) -> AuditLog:
 286     """Create an audit log entry."""
 287     audit_log = AuditLog(
 288         user_id=user_id,
 289         action=action,
 290         resource_type=resource_type,
 291         resource_id=resource_id,
 292         details=details,
 293         ip_address=ip_address,
 294         user_agent=user_agent,
 295     )
 296     db.add(audit_log)
 297     await db.flush()
 298     await db.refresh(audit_log)
 299     return audit_log
 300 
 301 
 302 async def list_audit_logs(
 303     db: AsyncSession,
 304     skip: int = 0,
 305     limit: int = 100,
 306     user_id: Optional[UUID] = None,
 307     action: Optional[str] = None,
 308     resource_type: Optional[str] = None,
 309     start_date: Optional[datetime] = None,
 310     end_date: Optional[datetime] = None,
 311 ) -> tuple[List[AuditLog], int]:
 312     """List audit logs with filtering and pagination."""
 313     query = select(AuditLog)
 314     
 315     if user_id:
 316         query = query.filter(AuditLog.user_id == user_id)
 317     if action:
 318         query = query.filter(AuditLog.action == action)
 319     if resource_type:
 320         query = query.filter(AuditLog.resource_type == resource_type)
 321     if start_date:
 322         query = query.filter(AuditLog.created_at >= start_date)
 323     if end_date:
 324         query = query.filter(AuditLog.created_at <= end_date)
 325     
 326     query = query.order_by(AuditLog.created_at.desc())
 327     
 328     # Get total count
 329     count_query = select(func.count()).select_from(query.subquery())
 330     total_result = await db.execute(count_query)
 331     total = total_result.scalar()
 332     
 333     # Get paginated results
 334     query = query.offset(skip).limit(limit)
 335     result = await db.execute(query)
 336     logs = result.scalars().all()
 337     
 338     return list(logs), total
 339 
 340 
 341 # Team operations
 342 
 343 async def create_team(
 344     db: AsyncSession,
 345     name: str,
 346     description: Optional[str] = None,
 347     manager_id: Optional[UUID] = None,
 348 ) -> Team:
 349     """Create a new team."""
 350     team = Team(
 351         name=name,
 352         description=description,
 353         manager_id=manager_id,
 354     )
 355     db.add(team)
 356     await db.flush()
 357     await db.refresh(team)
 358     return team
 359 
 360 
 361 async def get_team_by_id(db: AsyncSession, team_id: UUID) -> Optional[Team]:
 362     """Get team by ID."""
 363     result = await db.execute(select(Team).filter(Team.id == team_id))
 364     return result.scalar_one_or_none()
 365 
 366 
 367 async def list_teams(db: AsyncSession, skip: int = 0, limit: int = 100) -> tuple[List[Team], int]:
 368     """List all teams."""
 369     query = select(Team)
 370     
 371     # Get total count
 372     count_query = select(func.count()).select_from(Team)
 373     total_result = await db.execute(count_query)
 374     total = total_result.scalar()
 375     
 376     # Get paginated results
 377     query = query.offset(skip).limit(limit)
 378     result = await db.execute(query)
 379     teams = result.scalars().all()
 380     
 381     return list(teams), total
