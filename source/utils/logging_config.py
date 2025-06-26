"""
통합 로깅 시스템 설정
"""
import logging
import sys
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """컬러 로그 포매터"""
    
    # ANSI 색상 코드
    COLORS = {
        'DEBUG': '\033[36m',    # 청록색
        'INFO': '\033[32m',     # 녹색
        'WARNING': '\033[33m',  # 노란색
        'ERROR': '\033[31m',    # 빨간색
        'CRITICAL': '\033[35m', # 자주색
        'RESET': '\033[0m'      # 리셋
    }
    
    def format(self, record):
        # 색상 추가
        if hasattr(record, 'levelname'):
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class LoggingConfig:
    """로깅 설정 클래스"""
    
    def __init__(self, 
                 log_level: str = "INFO",
                 log_dir: str = "logs",
                 app_name: str = "scenario_helper"):
        self.log_level = getattr(logging, log_level.upper())
        self.log_dir = log_dir
        self.app_name = app_name
        
        # 로그 디렉토리 생성
        os.makedirs(log_dir, exist_ok=True)
    
    def setup_logging(self) -> logging.Logger:
        """로깅 시스템 설정"""
        
        # 루트 로거 설정
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # 기존 핸들러 제거
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 포매터 설정
        detailed_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(funcName)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        colored_formatter = ColoredFormatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # 1. 콘솔 핸들러 (컬러)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(colored_formatter)
        root_logger.addHandler(console_handler)
        
        # 2. 전체 로그 파일 (회전)
        all_logs_file = os.path.join(self.log_dir, f"{self.app_name}.log")
        file_handler = RotatingFileHandler(
            all_logs_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
        
        # 3. 에러 전용 로그 파일
        error_file = os.path.join(self.log_dir, f"{self.app_name}_error.log")
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=5*1024*1024,   # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
        
        # 4. 일별 로그 파일
        daily_file = os.path.join(self.log_dir, f"{self.app_name}_daily.log")
        daily_handler = TimedRotatingFileHandler(
            daily_file,
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        daily_handler.setLevel(logging.INFO)
        daily_handler.setFormatter(simple_formatter)
        root_logger.addHandler(daily_handler)
        
        # 특정 로거 설정
        self._setup_specific_loggers()
        
        # 시작 로그
        logger = logging.getLogger(__name__)
        logger.info(f"로깅 시스템 초기화 완료 - Level: {logging.getLevelName(self.log_level)}")
        
        return root_logger
    
    def _setup_specific_loggers(self):
        """특정 모듈별 로거 설정"""
        
        # LLM 관련 로거
        llm_logger = logging.getLogger('source.models.llm_handler')
        llm_file = os.path.join(self.log_dir, 'llm_operations.log')
        llm_handler = RotatingFileHandler(
            llm_file,
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        llm_handler.setLevel(logging.DEBUG)
        llm_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | LLM | %(message)s'
        ))
        llm_logger.addHandler(llm_handler)
        
        # API 관련 로거
        api_logger = logging.getLogger('uvicorn')
        api_logger.setLevel(logging.INFO)
        
        # 보안 관련 로거
        security_logger = logging.getLogger('source.utils.security')
        security_file = os.path.join(self.log_dir, 'security.log')
        security_handler = RotatingFileHandler(
            security_file,
            maxBytes=5*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | SECURITY | %(message)s | %(pathname)s:%(lineno)d'
        ))
        security_logger.addHandler(security_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """특정 이름의 로거 반환"""
        return logging.getLogger(name)


class PerformanceLogger:
    """성능 측정 로거"""
    
    def __init__(self, logger_name: str = "performance"):
        self.logger = logging.getLogger(logger_name)
        self.start_times = {}
    
    def start_timer(self, operation: str):
        """타이머 시작"""
        import time
        self.start_times[operation] = time.time()
        self.logger.debug(f"Started: {operation}")
    
    def end_timer(self, operation: str, extra_info: Optional[str] = None):
        """타이머 종료 및 로그"""
        import time
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            info = f" | {extra_info}" if extra_info else ""
            self.logger.info(f"Completed: {operation} | Duration: {duration:.3f}s{info}")
            del self.start_times[operation]
            return duration
        return None


# 전역 로깅 설정
def setup_global_logging(log_level: str = "INFO") -> logging.Logger:
    """전역 로깅 설정"""
    config = LoggingConfig(log_level=log_level)
    return config.setup_logging()


# 환경변수에서 로그 레벨 읽기
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 자동 초기화 (임포트시)
if __name__ != "__main__":
    try:
        setup_global_logging(LOG_LEVEL)
    except Exception as e:
        print(f"로깅 초기화 실패: {e}")


if __name__ == "__main__":
    # 테스트 코드
    logger = setup_global_logging("DEBUG")
    
    test_logger = logging.getLogger("test")
    test_logger.debug("디버그 메시지")
    test_logger.info("정보 메시지")
    test_logger.warning("경고 메시지")
    test_logger.error("에러 메시지")
    test_logger.critical("심각한 에러")
    
    # 성능 로거 테스트
    perf_logger = PerformanceLogger()
    perf_logger.start_timer("test_operation")
    import time
    time.sleep(0.1)
    perf_logger.end_timer("test_operation", "테스트 완료")
