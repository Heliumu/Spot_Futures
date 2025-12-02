import os
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class PromptLoader:
    """Prompt加载器，统一管理所有Prompt文件"""
    
    def __init__(self, prompt_dir: str = "prompts"):
        """
        初始化Prompt加载器
        
        Args:
            prompt_dir: Prompt文件所在目录
        """
        self.prompt_dir = prompt_dir
        self._prompts: Dict[str, str] = {}
        self.load_all_prompts()
    
    def load_all_prompts(self):
        """加载所有prompt文件"""
        if not os.path.exists(self.prompt_dir):
            raise FileNotFoundError(f"Prompt目录不存在: {self.prompt_dir}")
        
        loaded_count = 0
        for filename in os.listdir(self.prompt_dir):
            if filename.endswith('.txt'):
                prompt_name = filename[:-4]  # 去掉.txt后缀
                filepath = os.path.join(self.prompt_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self._prompts[prompt_name] = f.read().strip()
                        loaded_count += 1
                        logger.debug(f"已加载Prompt: {prompt_name}")
                except Exception as e:
                    logger.error(f"加载Prompt文件失败 {filepath}: {e}")
                    raise
        
        logger.info(f"成功加载 {loaded_count} 个Prompt文件")
    
    def get_prompt(self, name: str) -> str:
        """
        获取指定的prompt
        
        Args:
            name: Prompt名称
            
        Returns:
            Prompt内容
            
        Raises:
            ValueError: 如果Prompt未找到
        """
        if name not in self._prompts:
            available_prompts = ', '.join(self._prompts.keys())
            raise ValueError(f"Prompt未找到: {name}。可用的Prompt: {available_prompts}")
        return self._prompts[name]
    
    def format_prompt(self, name: str, **kwargs) -> str:
        """
        格式化prompt
        
        Args:
            name: Prompt名称
            **kwargs: 格式化参数
            
        Returns:
            格式化后的Prompt
            
        Raises:
            ValueError: 如果格式化失败
        """
        prompt = self.get_prompt(name)
        
        try:
            return prompt.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"格式化prompt失败，缺少参数: {e}")
        except Exception as e:
            raise ValueError(f"格式化prompt失败: {e}")
    
    def reload(self):
        """重新加载所有Prompt"""
        logger.info("重新加载Prompt...")
        self._prompts.clear()
        self.load_all_prompts()
        logger.info("Prompt重新加载完成")
    
    def list_prompts(self) -> list:
        """获取所有可用的Prompt名称列表"""
        return list(self._prompts.keys())
    
    def get_prompt_info(self, name: str) -> dict:
        """
        获取Prompt信息
        
        Args:
            name: Prompt名称
            
        Returns:
            包含Prompt信息的字典
        """
        if name not in self._prompts:
            raise ValueError(f"Prompt未找到: {name}")
        
        content = self._prompts[name]
        return {
            "name": name,
            "length": len(content),
            "lines": content.count('\n') + 1,
            "preview": content[:100] + "..." if len(content) > 100 else content
        }


# 创建全局Prompt加载器实例
try:
    prompt_loader = PromptLoader()
    logger.info("全局Prompt加载器初始化成功")
except Exception as e:
    logger.error(f"全局Prompt加载器初始化失败: {e}")
    # 创建一个空的加载器以避免程序崩溃
    prompt_loader = PromptLoader.__new__(PromptLoader)
    prompt_loader._prompts = {}
    logger.warning("使用空的Prompt加载器，请检查Prompt文件")


# 便捷函数
def get_prompt(name: str) -> str:
    """便捷函数：获取Prompt"""
    return prompt_loader.get_prompt(name)


def format_prompt(name: str, **kwargs) -> str:
    """便捷函数：格式化Prompt"""
    return prompt_loader.format_prompt(name, **kwargs)


def reload_prompts():
    """便捷函数：重新加载Prompt"""
    prompt_loader.reload()


def list_prompts() -> list:
    """便捷函数：获取所有Prompt名称"""
    return prompt_loader.list_prompts()


if __name__ == "__main__":
    # 测试代码
    import sys
    
    # 设置日志级别
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 列出所有Prompt
    print("可用的Prompt:")
    for prompt_name in list_prompts():
        info = prompt_loader.get_prompt_info(prompt_name)
        print(f"  - {prompt_name}: {info['length']} 字符, {info['lines']} 行")
    
    # 测试格式化
    if len(sys.argv) > 1:
        prompt_name = sys.argv[1]
        try:
            formatted = format_prompt(prompt_name, commodity_name="豆粕", content="测试内容")
            print(f"\n格式化后的 {prompt_name}:")
            print(formatted[:500] + "..." if len(formatted) > 500 else formatted)
        except Exception as e:
            print(f"格式化失败: {e}")
