import threading
import math
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, Column, BigInteger, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.pool import StaticPool
from bot.config import DB

BASE = declarative_base()


class FileStats(BASE):
    __tablename__ = "file_stats"
    date = Column(Date, primary_key=True)
    total_files = Column(BigInteger, default=0)
    total_size = Column(BigInteger, default=0)

    def __init__(self, date, total_files=0, total_size=0):
        self.date = date
        self.total_files = total_files
        self.total_size = total_size


def start() -> scoped_session:
    engine = create_engine(DB.DB_URL, client_encoding="utf8", poolclass=StaticPool)
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


SESSION = start()
INSERTION_LOCK = threading.RLock()


def get_current_gmt_date():
    return datetime.now(timezone.utc).date()


async def add_file_size(file_size: int):
    with INSERTION_LOCK:
        try:
            today = get_current_gmt_date()
            try:
                stats = SESSION.query(FileStats).filter_by(date=today).one()
                stats.total_files += 1
                stats.total_size += file_size
            except NoResultFound:
                stats = FileStats(date=today, total_files=1, total_size=file_size)
                SESSION.add(stats)

            SESSION.commit()
        except Exception as e:
            SESSION.rollback()
            raise e
        finally:
            SESSION.close()


async def get_total_stats():
    try:
        result = SESSION.query(
            func.sum(FileStats.total_files).label("total_files"),
            func.sum(FileStats.total_size).label("total_size"),
        ).first()
        total_files = int(result.total_files) if result.total_files else 0
        total_size = int(result.total_size) if result.total_size else 0

        return total_files, total_size
    except Exception:
        return 0, 0
    finally:
        SESSION.close()


async def get_today_stats():
    try:
        today = get_current_gmt_date()
        stats = SESSION.query(FileStats).filter_by(date=today).first()

        if stats:
            return int(stats.total_files), int(stats.total_size)
        return 0, 0
    except Exception:
        return 0, 0
    finally:
        SESSION.close()


async def get_yesterday_stats():
    try:
        yesterday = get_current_gmt_date() - timedelta(days=1)
        stats = SESSION.query(FileStats).filter_by(date=yesterday).first()

        if stats:
            return int(stats.total_files), int(stats.total_size)
        return 0, 0
    except Exception:
        return 0, 0
    finally:
        SESSION.close()


async def get_last_7_days_stats():
    try:
        seven_days_ago = get_current_gmt_date() - timedelta(days=7)
        today = get_current_gmt_date()
        result = (
            SESSION.query(
                func.sum(FileStats.total_files).label("total_files"),
                func.sum(FileStats.total_size).label("total_size"),
            )
            .filter(FileStats.date >= seven_days_ago, FileStats.date <= today)
            .first()
        )
        total_files = int(result.total_files) if result.total_files else 0
        total_size = int(result.total_size) if result.total_size else 0

        return total_files, total_size
    except Exception:
        return 0, 0
    finally:
        SESSION.close()


def format_file_size(size_bytes) -> str:
    try:
        size_bytes = float(size_bytes) if size_bytes else 0.0
    except (ValueError, TypeError):
        return "0 B"
    
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


async def get_formatted_stats():
    total_files, total_size = await get_total_stats()
    today_files, today_size = await get_today_stats()
    yesterday_files, yesterday_size = await get_yesterday_stats()
    week_files, week_size = await get_last_7_days_stats()
    return {
        "total_files": total_files,
        "total_size": format_file_size(total_size),
        "today_files": today_files,
        "today_size": format_file_size(today_size),
        "yesterday_files": yesterday_files,
        "yesterday_size": format_file_size(yesterday_size),
        "week_files": week_files,
        "week_size": format_file_size(week_size),
    }
