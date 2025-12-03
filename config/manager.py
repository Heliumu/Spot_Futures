# config/manager.py
"""
配置管理器
支持多环境配置、环境变量替换、动态重载等功能
"""

import os
import re
import toml
from typing import Any, Optional, Dict, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器，支持环境变量和多环境配置"""
    
    def __init__(self, config_path: str = "config/settings.toml"):
        """
        初始化配置管理器
        
        Args:
            config_path: TOML 配置文件路径
        """
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._env_vars: Dict[str, str] = {}
        
        # 加载所有环境变量和配置
        self._load_all()
    
    def _load_all(self):
        """加载所有环境变量和配置文件"""
        try:
            self._load_env_vars()
            self.load_config()
            logger.info("配置加载成功")
        except Exception as e:
            logger.error(f"配置加载失败: {e}")
            raise
    
    def _load_env_vars(self):
        """加载环境变量，优先级：系统环境变量 < .env < .env.{environment}"""
        # 1. 首先加载系统环境变量
        self._env_vars.update(dict(os.environ))
        
        # 2. 加载根目录的 .env 文件
        self._load_env_file(Path(".env"))
        
        # 3. 加载环境特定的 .env 文件
        env = os.getenv("ENVIRONMENT", "development")
        self._load_env_file(Path(f"config/.env.{env}"))
        
        # 4. 加载用户自定义的环境文件
        custom_env = os.getenv("ENV_FILE")
        if custom_env:
            self._load_env_file(Path(custom_env))
        
        logger.debug(f"已加载 {len(self._env_vars)} 个环境变量")
    
    def _load_env_file(self, env_file: Path):
        """加载单个 .env 文件"""
        if not env_file.exists():
            logger.debug(f"环境文件不存在: {env_file}")
            return
        
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # 跳过空行和注释
                    if not line or line.startswith('#'):
                        continue
                    
                    # 解析键值对
                    if '=' in line:
                        # 支持带引号的值
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # 移除引号
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        
                        self._env_vars[key] = value
                    else:
                        logger.warning(f"{env_file}:{line_num} - 无效的行: {line}")
            
            logger.debug(f"从 {env_file} 加载了环境变量")
        except Exception as e:
            logger.error(f"加载环境文件失败 {env_file}: {e}")
            raise
    
    def _substitute_env_vars(self, value: Any) -> Any:
        """
        递归替换配置中的环境变量
        支持 ${VAR_NAME} 和 $VAR_NAME 两种格式
        """
        if isinstance(value, str):
            # 匹配 ${VAR_NAME} 和 $VAR_NAME 格式
            pattern = r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)'
            
            def replace_var(match):
                # 获取变量名（两种格式之一）
                var_name = match.group(1) or match.group(2)
                
                # 优先从加载的环境变量中获取
                if var_name in self._env_vars:
                    return self._env_vars[var_name]
                
                # 然后从系统环境变量获取
                if var_name in os.environ:
                    return os.environ[var_name]
                
                # 如果环境变量不存在，记录警告并保持原样
                logger.warning(f"环境变量未找到: {var_name}")
                return match.group(0)
            
            # 替换所有环境变量引用
            return re.sub(pattern, replace_var, value)
        elif isinstance(value, dict):
            return {k: self._substitute_env_vars(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._substitute_env_vars(item) for item in value]
        else:
            return value
    
    def load_config(self):
        """加载并处理 TOML 配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件未找到: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                raw_config = toml.load(f)
                self._config = self._substitute_env_vars(raw_config)
                logger.debug(f"配置文件加载成功: {self.config_path}")
        except toml.TomlDecodeError as e:
            raise Exception(f"TOML 文件格式错误: {e}")
        except Exception as e:
            raise Exception(f"加载配置文件失败: {e}")
    
    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            section: 配置节名
            key: 配置键名，如果为 None 则返回整个节
            default: 默认值
            
        Returns:
            配置值
        """
        try:
            section_data = self._config.get(section, {})
            
            if key is None:
                return section_data if section_data else default
            
            return section_data.get(key, default)
        except Exception as e:
            logger.error(f"获取配置失败 [{section}][{key}]: {e}")
            return default
    
    def get_llm_config(self, provider: str) -> Dict[str, Any]:
        """
        获取特定 LLM 提供商的配置
        
        Args:
            provider: LLM 提供商名称
            
        Returns:
            LLM 配置字典
            
        Raises:
            ValueError: 当配置不存在或无效时
        """
        config = self.get('llm_providers', provider, {})
        
        if not config:
            raise ValueError(f"未找到提供商 {provider} 的配置")
        
        # 验证必需的配置项
        required_fields = ['api_key', 'base_url', 'model']
        missing_fields = [field for field in required_fields if not config.get(field)]
        
        if missing_fields:
            raise ValueError(
                f"提供商 {provider} 缺少必需的配置项: {', '.join(missing_fields)}"
            )
        
        # 验证 API Key 不是占位符
        api_key = config['api_key']
        if api_key.startswith('${') or not api_key.strip():
            raise ValueError(f"提供商 {provider} 的 API_KEY 未正确配置")
        
        # 设置默认值
        config.setdefault('temperature', 0.7)
        config.setdefault('max_tokens', 1024)
        
        return config
    
    def get_all_llm_providers(self) -> Dict[str, Dict[str, Any]]:
        """获取所有 LLM 提供商的配置"""
        return self.get('llm_providers', default={})
    
    def get_default_llm_provider(self) -> str:
        """获取默认的 LLM 提供商"""
        return self.get('llm', 'default_provider', 'zhipu')
    
    def is_debug_enabled(self) -> bool:
        """检查是否启用调试模式"""
        return self.get('debug', 'enabled', False)
    
    def get_debug_port(self) -> int:
        """获取调试端口"""
        return self.get('debug', 'port', 5173)
    
    def reload(self):
        """重新加载所有配置"""
        logger.info("重新加载配置...")
        self._config.clear()
        self._env_vars.clear()
        self._load_all()
        logger.info("配置重新加载完成")
    
    def validate_config(self) -> Dict[str, Any]:
        """
        验证配置完整性
        
        Returns:
            验证结果字典
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # 验证 LLM 配置
            llm_providers = self.get_all_llm_providers()
            if not llm_providers:
                result['errors'].append("未找到任何 LLM 提供商配置")
                result['valid'] = False
            else:
                for provider in llm_providers:
                    try:
                        self.get_llm_config(provider)
                    except ValueError as e:
                        result['errors'].append(str(e))
                        result['valid'] = False
            
            # 验证默认提供商
            try:
                default_provider = self.get_default_llm_provider()
                if default_provider not in llm_providers:
                    result['warnings'].append(
                        f"默认提供商 '{default_provider}' 未在 llm_providers 中配置"
                    )
            except Exception as e:
                result['warnings'].append(f"获取默认提供商失败: {e}")
            
        except Exception as e:
            result['errors'].append(f"配置验证失败: {e}")
            result['valid'] = False
        
        return result
    
    def print_config_summary(self):
        """打印配置摘要（隐藏敏感信息）"""
        print("\n=== 配置摘要 ===")
        
        # LLM 提供商
        print(f"\nLLM 提供商:")
        providers = self.get_all_llm_providers()
        for name, config in providers.items():
            api_key = config.get('api_key', '')
            key_preview = f"{api_key[:8]}..." if len(api_key) > 8 else "***"
            print(f"  - {name}: {config.get('model', 'N/A')} (Key: {key_preview})")
        
        # 默认提供商
        print(f"\n默认提供商: {self.get_default_llm_provider()}")
        
        # 调试配置
        print(f"\n调试模式: {'启用' if self.is_debug_enabled() else '禁用'}")
        if self.is_debug_enabled():
            print(f"调试端口: {self.get_debug_port()}")
        
        # 环境信息
        print(f"\n环境信息:")
        print(f"  - ENVIRONMENT: {os.getenv('ENVIRONMENT', 'development')}")
        print(f"  - ENV_FILE: {os.getenv('ENV_FILE', 'N/A')}")
        
        print("=" * 50 + "\n")
    
    def export_env_template(self, output_path: str = "config/.env.example"):
        """
        导出环境变量模板文件
        
        Args:
            output_path: 输出文件路径
        """
        env_vars = set()
        
        # 从配置中提取所有环境变量引用
        def collect_env_vars(obj):
            if isinstance(obj, str):
                # 查找 ${VAR_NAME} 和 $VAR_NAME 格式
                matches = re.findall(r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)', obj)
                for match in matches:
                    var_name = match[0] or match[1]
                    if var_name:
                        env_vars.add(var_name)
            elif isinstance(obj, dict):
                for v in obj.values():
                    collect_env_vars(v)
            elif isinstance(obj, list):
                for item in obj:
                    collect_env_vars(item)
        
        collect_env_vars(self._config)
        
        # 写入模板文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 环境变量模板文件\n")
            f.write("# 复制此文件为 .env 并填入实际值\n\n")
            
            for var in sorted(env_vars):
                f.write(f"{var}=your_{var.lower()}_here\n")
        
        logger.info(f"环境变量模板已导出到: {output_path}")


# 创建全局配置管理器实例
try:
    config_manager = ConfigManager()
    logger.info("全局配置管理器初始化成功")
except Exception as e:
    logger.error(f"全局配置管理器初始化失败: {e}")
    # 创建一个最小的配置管理器以避免程序崩溃
    config_manager = ConfigManager.__new__(ConfigManager)
    config_manager._config = {}
    config_manager._env_vars = {}
    logger.warning("使用空的配置管理器，请检查配置文件")


# 便捷函数
def get_config(section: str, key: str = None, default: Any = None) -> Any:
    """便捷函数：获取配置值"""
    return config_manager.get(section, key, default)


def get_llm_config(provider: str) -> Dict[str, Any]:
    """便捷函数：获取 LLM 配置"""
    return config_manager.get_llm_config(provider)


def reload_config():
    """便捷函数：重新加载配置"""
    config_manager.reload()


if __name__ == "__main__":
    # 测试代码
    import sys
    
    # 设置日志级别
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 打印配置摘要
    config_manager.print_config_summary()
    
    # 验证配置
    validation = config_manager.validate_config()
    print(f"\n配置验证结果: {'通过' if validation['valid'] else '失败'}")
    
    if validation['errors']:
        print("\n错误:")
        for error in validation['errors']:
            print(f"  - {error}")
    
    if validation['warnings']:
        print("\n警告:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    # 导出环境变量模板
    if len(sys.argv) > 1 and sys.argv[1] == '--export-env':
        config_manager.export_env_template()
