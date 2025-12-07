"""
Генератор HTML-отчета в стиле Allure из JSON результатов.
Создает красивый отчет без необходимости установки Java и Allure CLI.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class AllureReportGenerator:
    """Генератор HTML-отчета в стиле Allure."""
    
    def __init__(self, results_dir: str, output_file: str = "allure_report.html"):
        self.results_dir = Path(results_dir)
        self.output_file = output_file
        self.results = []
        self.containers = []
        self.attachments = {}
        
    def load_results(self):
        """Загружает все результаты тестов из JSON файлов."""
        for file in self.results_dir.glob("*-result.json"):
            with open(file, 'r', encoding='utf-8') as f:
                self.results.append(json.load(f))
        
        for file in self.results_dir.glob("*-container.json"):
            with open(file, 'r', encoding='utf-8') as f:
                self.containers.append(json.load(f))
                
        # Загружаем текстовые attachments
        for file in self.results_dir.glob("*-attachment.txt"):
            with open(file, 'r', encoding='utf-8') as f:
                self.attachments[file.name] = f.read()
    
    def get_status_color(self, status: str) -> str:
        """Возвращает цвет для статуса теста."""
        colors = {
            'passed': '#4caf50',
            'failed': '#f44336',
            'broken': '#ff9800',
            'skipped': '#9e9e9e',
            'unknown': '#607d8b'
        }
        return colors.get(status.lower(), '#607d8b')
    
    def get_status_icon(self, status: str) -> str:
        """Возвращает иконку для статуса теста."""
        icons = {
            'passed': '✓',
            'failed': '✗',
            'broken': '⚠',
            'skipped': '○',
            'unknown': '?'
        }
        return icons.get(status.lower(), '?')
    
    def format_duration(self, duration_ms: int) -> str:
        """Форматирует длительность теста."""
        if duration_ms < 1000:
            return f"{duration_ms}ms"
        seconds = duration_ms / 1000
        if seconds < 60:
            return f"{seconds:.2f}s"
        minutes = int(seconds / 60)
        seconds = seconds % 60
        return f"{minutes}m {seconds:.2f}s"
    
    def get_statistics(self) -> Dict[str, int]:
        """Подсчитывает статистику по тестам."""
        stats = {'passed': 0, 'failed': 0, 'broken': 0, 'skipped': 0, 'unknown': 0, 'total': 0}
        for result in self.results:
            status = result.get('status', 'unknown').lower()
            stats[status] = stats.get(status, 0) + 1
            stats['total'] += 1
        return stats
    
    def generate_html(self) -> str:
        """Генерирует HTML-отчет."""
        stats = self.get_statistics()
        total_duration = sum(r.get('stop', 0) - r.get('start', 0) for r in self.results)
        
        # Сортируем результаты: сначала failed, потом passed
        sorted_results = sorted(self.results, key=lambda x: (
            0 if x.get('status') == 'failed' else 1 if x.get('status') == 'broken' else 2
        ))
        
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Allure Report - Test Results</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .header h1 {{
            font-size: 32px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .logo {{
            width: 50px;
            height: 50px;
            background: white;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
        }}
        
        .header-info {{
            text-align: right;
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 40px;
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }}
        
        .stat-card h3 {{
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .stat-icon {{
            font-size: 24px;
        }}
        
        .tests-container {{
            padding: 40px;
        }}
        
        .test-card {{
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            margin-bottom: 20px;
            overflow: hidden;
            transition: all 0.3s;
        }}
        
        .test-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-color: #667eea;
        }}
        
        .test-header {{
            padding: 20px 25px;
            background: #fafafa;
            border-bottom: 1px solid #e0e0e0;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.2s;
        }}
        
        .test-header:hover {{
            background: #f0f0f0;
        }}
        
        .test-title {{
            display: flex;
            align-items: center;
            gap: 15px;
            flex: 1;
        }}
        
        .status-badge {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: bold;
            color: white;
        }}
        
        .test-name {{
            font-size: 16px;
            font-weight: 500;
            color: #333;
        }}
        
        .test-meta {{
            display: flex;
            gap: 20px;
            align-items: center;
            font-size: 14px;
            color: #666;
        }}
        
        .duration {{
            background: #e3f2fd;
            color: #1976d2;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: 500;
        }}
        
        .test-body {{
            padding: 25px;
            display: none;
            background: white;
        }}
        
        .test-body.active {{
            display: block;
            animation: slideDown 0.3s ease-out;
        }}
        
        @keyframes slideDown {{
            from {{
                opacity: 0;
                transform: translateY(-10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .test-section {{
            margin-bottom: 20px;
        }}
        
        .test-section h4 {{
            font-size: 14px;
            color: #667eea;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .test-steps {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .step {{
            padding: 8px 0;
            color: #555;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .step-icon {{
            color: #4caf50;
            font-weight: bold;
        }}
        
        .attachment {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
        }}
        
        .attachment-title {{
            font-weight: 600;
            color: #856404;
            margin-bottom: 8px;
        }}
        
        .attachment-content {{
            background: white;
            padding: 12px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            max-height: 300px;
            overflow-y: auto;
            color: #333;
        }}
        
        .error-message {{
            background: #ffebee;
            border-left: 4px solid #f44336;
            padding: 15px;
            border-radius: 8px;
            color: #c62828;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            white-space: pre-wrap;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #666;
            font-size: 14px;
            border-top: 1px solid #e0e0e0;
        }}
        
        .expand-icon {{
            transition: transform 0.3s;
            font-size: 20px;
            color: #999;
        }}
        
        .expand-icon.active {{
            transform: rotate(180deg);
        }}
        
        .labels {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }}
        
        .label {{
            background: #e3f2fd;
            color: #1976d2;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>
                <div class="logo">📊</div>
                Allure Test Report
            </h1>
            <div class="header-info">
                <div>Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</div>
                <div>Всего тестов: {stats['total']}</div>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Всего тестов</h3>
                <div class="stat-value" style="color: #667eea;">
                    <span class="stat-icon">📝</span>
                    {stats['total']}
                </div>
            </div>
            
            <div class="stat-card">
                <h3>Успешно</h3>
                <div class="stat-value" style="color: #4caf50;">
                    <span class="stat-icon">✓</span>
                    {stats['passed']}
                </div>
            </div>
            
            <div class="stat-card">
                <h3>Провалено</h3>
                <div class="stat-value" style="color: #f44336;">
                    <span class="stat-icon">✗</span>
                    {stats['failed']}
                </div>
            </div>
            
            <div class="stat-card">
                <h3>Пропущено</h3>
                <div class="stat-value" style="color: #9e9e9e;">
                    <span class="stat-icon">○</span>
                    {stats['skipped']}
                </div>
            </div>
            
            <div class="stat-card">
                <h3>Длительность</h3>
                <div class="stat-value" style="color: #ff9800;">
                    <span class="stat-icon">⏱</span>
                    {self.format_duration(total_duration)}
                </div>
            </div>
        </div>
        
        <div class="tests-container">
            <h2 style="margin-bottom: 25px; color: #333; font-size: 24px;">Результаты тестов</h2>
"""
        
        # Генерируем карточки для каждого теста
        for idx, result in enumerate(sorted_results):
            status = result.get('status', 'unknown').lower()
            name = result.get('name', 'Unknown Test')
            full_name = result.get('fullName', name)
            duration = result.get('stop', 0) - result.get('start', 0)
            
            # Получаем шаги теста
            steps = result.get('steps', [])
            
            # Получаем labels
            labels = result.get('labels', [])
            
            # Получаем attachments
            attachments = result.get('attachments', [])
            
            # Получаем информацию об ошибке
            status_details = result.get('statusDetails', {})
            error_message = status_details.get('message', '')
            error_trace = status_details.get('trace', '')
            
            html += f"""
            <div class="test-card">
                <div class="test-header" onclick="toggleTest({idx})">
                    <div class="test-title">
                        <div class="status-badge" style="background-color: {self.get_status_color(status)};">
                            {self.get_status_icon(status)}
                        </div>
                        <div>
                            <div class="test-name">{name}</div>
                            <div style="font-size: 12px; color: #999; margin-top: 5px;">{full_name}</div>
                        </div>
                    </div>
                    <div class="test-meta">
                        <span class="duration">{self.format_duration(duration)}</span>
                        <span class="expand-icon" id="icon-{idx}">▼</span>
                    </div>
                </div>
                <div class="test-body" id="body-{idx}">
"""
            
            # Добавляем labels
            if labels:
                html += """
                    <div class="test-section">
                        <h4>Метки</h4>
                        <div class="labels">
"""
                for label in labels:
                    label_name = label.get('name', '')
                    label_value = label.get('value', '')
                    html += f'<span class="label">{label_name}: {label_value}</span>'
                html += """
                        </div>
                    </div>
"""
            
            # Добавляем шаги
            if steps:
                html += """
                    <div class="test-section">
                        <h4>Шаги выполнения</h4>
                        <div class="test-steps">
"""
                for step in steps:
                    step_name = step.get('name', 'Unknown Step')
                    step_status = step.get('status', 'passed')
                    step_icon = '✓' if step_status == 'passed' else '✗'
                    step_color = '#4caf50' if step_status == 'passed' else '#f44336'
                    html += f'<div class="step"><span class="step-icon" style="color: {step_color};">{step_icon}</span> {step_name}</div>'
                html += """
                        </div>
                    </div>
"""
            
            # Добавляем ошибку, если есть
            if error_message or error_trace:
                html += """
                    <div class="test-section">
                        <h4>Информация об ошибке</h4>
"""
                if error_message:
                    html += f'<div class="error-message">{error_message}</div>'
                if error_trace:
                    html += f'<div class="error-message" style="margin-top: 10px;">{error_trace}</div>'
                html += """
                    </div>
"""
            
            # Добавляем attachments
            if attachments:
                html += """
                    <div class="test-section">
                        <h4>Вложения</h4>
"""
                for attachment in attachments:
                    att_name = attachment.get('name', 'Attachment')
                    att_source = attachment.get('source', '')
                    att_type = attachment.get('type', 'text/plain')
                    
                    # Если это текстовый файл, показываем его содержимое
                    if att_source in self.attachments:
                        content = self.attachments[att_source]
                        html += f"""
                        <div class="attachment">
                            <div class="attachment-title">📎 {att_name}</div>
                            <div class="attachment-content">{content}</div>
                        </div>
"""
                html += """
                    </div>
"""
            
            html += """
                </div>
            </div>
"""
        
        html += """
        </div>
        
        <div class="footer">
            <p>Отчет сгенерирован автоматически | PetStore API Testing Project</p>
            <p style="margin-top: 5px; font-size: 12px;">Powered by Allure Framework & Custom HTML Generator</p>
        </div>
    </div>
    
    <script>
        function toggleTest(index) {
            const body = document.getElementById('body-' + index);
            const icon = document.getElementById('icon-' + index);
            
            body.classList.toggle('active');
            icon.classList.toggle('active');
        }
    </script>
</body>
</html>
"""
        return html
    
    def generate(self):
        """Генерирует и сохраняет HTML-отчет."""
        print("🔄 Загрузка результатов тестов...")
        self.load_results()
        
        print(f"✓ Загружено {len(self.results)} тестов")
        print(f"✓ Загружено {len(self.containers)} контейнеров")
        print(f"✓ Загружено {len(self.attachments)} вложений")
        
        print("\n🔄 Генерация HTML-отчета...")
        html_content = self.generate_html()
        
        output_path = Path(self.output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n✅ HTML-отчет успешно создан: {output_path.absolute()}")
        print(f"📊 Откройте файл в браузере для просмотра результатов")
        
        return output_path.absolute()


if __name__ == "__main__":
    # Генерируем отчет
    generator = AllureReportGenerator(
        results_dir="allure-results",
        output_file="allure_report.html"
    )
    
    try:
        report_path = generator.generate()
        print(f"\n{'='*60}")
        print(f"🎉 Отчет готов!")
        print(f"{'='*60}")
    except Exception as e:
        print(f"\n❌ Ошибка при генерации отчета: {e}")
        import traceback
        traceback.print_exc()
