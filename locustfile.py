"""
Конфигурация нагрузочного тестирования Locust для API глоссария.

Этот файл определяет поведение пользователей для нагрузочного тестирования FastAPI приложения.
Запуск: locust -f locustfile.py --host=http://localhost:8000

Сценарии тестирования:
1. Легкая нагрузка: 10 users, spawn-rate 2, 1 min
2. Рабочая нагрузка: 50 users, spawn-rate 5, 3 min
3. Стресс-тест: 200 users, spawn-rate 20, 5 min
4. Тест на стабильность: 50 users, spawn-rate 5, 10 min
"""

from locust import HttpUser, task, between, events
import random
import string
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Счетчики для статистики
stats = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "created_terms": 0,
    "updated_terms": 0,
    "deleted_terms": 0,
}


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Вызывается при старте теста"""
    logger.info("=" * 80)
    logger.info("Starting load test for Glossary API")
    logger.info(f"Host: {environment.host}")
    logger.info("=" * 80)
    stats.update({
        "total_requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "created_terms": 0,
        "updated_terms": 0,
        "deleted_terms": 0,
    })


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Вызывается при завершении теста"""
    logger.info("=" * 80)
    logger.info("Load test completed")
    logger.info(f"Total requests: {stats['total_requests']}")
    logger.info(f"Successful: {stats['successful_requests']}")
    logger.info(f"Failed: {stats['failed_requests']}")
    logger.info(f"Terms created: {stats['created_terms']}")
    logger.info(f"Terms updated: {stats['updated_terms']}")
    logger.info(f"Terms deleted: {stats['deleted_terms']}")
    logger.info("=" * 80)


class GlossaryUser(HttpUser):
    """
    Симулирует пользователя, взаимодействующего с API глоссария.

    Пользователь выполняет различные операции: чтение терминов, создание новых,
    обновление существующих и их удаление.
    """

    # Время ожидания между задачами (1-3 секунды)
    wait_time = between(1, 3)

    def on_start(self):
        """
        Вызывается при старте симулированного пользователя.
        Инициализирует список для отслеживания созданных keywords для последующей очистки.
        """
        self.created_keywords = []
        # Получаем существующие термины для работы с ними
        response = self.client.get("/terms")
        if response.status_code == 200:
            terms = response.json()
            self.existing_keywords = [term["keyword"] for term in terms] if terms else []
        else:
            self.existing_keywords = []

    @task(10)
    def list_terms(self):
        """
        Самая частая операция: получение списка всех терминов.
        Вес: 10 (высокая частота)
        """
        response = self.client.get("/terms", name="/terms [LIST]")
        stats["total_requests"] += 1
        if response.status_code == 200:
            stats["successful_requests"] += 1
        else:
            stats["failed_requests"] += 1

    @task(8)
    def get_random_term(self):
        """
        Получение конкретного термина по keyword.
        Вес: 8
        """
        stats["total_requests"] += 1
        if self.existing_keywords:
            keyword = random.choice(self.existing_keywords)
            response = self.client.get(f"/terms/{keyword}", name="/terms/{keyword} [GET]")
            if response.status_code == 200:
                stats["successful_requests"] += 1
            else:
                stats["failed_requests"] += 1
        else:
            # Если терминов нет, получим 404
            self.client.get("/terms/nonexistent", name="/terms/{keyword} [GET 404]")
            stats["failed_requests"] += 1

    @task(3)
    def create_term(self):
        """
        Создание нового термина со случайными данными.
        Вес: 3 (менее частая операция)
        """
        keyword = self._generate_random_keyword()
        payload = {
            "keyword": keyword,
            "title": f"Test Term {keyword}",
            "description": f"This is a test description for {keyword}. It contains detailed information about the term."
        }

        response = self.client.post(
            "/terms",
            json=payload,
            name="/terms [CREATE]"
        )

        stats["total_requests"] += 1
        if response.status_code == 201:
            self.created_keywords.append(keyword)
            self.existing_keywords.append(keyword)
            stats["successful_requests"] += 1
            stats["created_terms"] += 1
        else:
            stats["failed_requests"] += 1

    @task(2)
    def update_term(self):
        """
        Обновление существующего термина.
        Вес: 2 (менее частая операция)
        """
        # Пытаемся обновить термин, который мы создали, или случайный существующий
        keywords_pool = self.created_keywords if self.created_keywords else self.existing_keywords

        if keywords_pool:
            keyword = random.choice(keywords_pool)
            payload = {
                "title": f"Updated Title {random.randint(1, 1000)}",
                "description": f"Updated description at {random.randint(1, 1000)}"
            }

            response = self.client.put(
                f"/terms/{keyword}",
                json=payload,
                name="/terms/{keyword} [UPDATE]"
            )

            stats["total_requests"] += 1
            if response.status_code == 200:
                stats["successful_requests"] += 1
                stats["updated_terms"] += 1
            else:
                stats["failed_requests"] += 1

    @task(1)
    def delete_term(self):
        """
        Удаление термина (только те, что созданы этим пользователем).
        Вес: 1 (самая редкая операция)
        """
        if self.created_keywords:
            keyword = self.created_keywords.pop()
            response = self.client.delete(
                f"/terms/{keyword}",
                name="/terms/{keyword} [DELETE]"
            )

            stats["total_requests"] += 1
            if response.status_code == 204:
                # Удаляем также из списка существующих keywords
                if keyword in self.existing_keywords:
                    self.existing_keywords.remove(keyword)
                stats["successful_requests"] += 1
                stats["deleted_terms"] += 1
            else:
                stats["failed_requests"] += 1

    @task(1)
    def get_nonexistent_term(self):
        """
        Намеренная попытка получить несуществующий термин для тестирования обработки ошибок.
        Вес: 1
        """
        fake_keyword = self._generate_random_keyword()
        response = self.client.get(
            f"/terms/{fake_keyword}",
            name="/terms/{keyword} [GET 404]"
        )
        stats["total_requests"] += 1
        # 404 - это ожидаемый ответ, не считаем его ошибкой
        if response.status_code == 404:
            stats["successful_requests"] += 1
        else:
            stats["failed_requests"] += 1

    def _generate_random_keyword(self):
        """Генерирует случайный keyword для тестирования."""
        return f"test_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"

    def on_stop(self):
        """
        Вызывается при остановке симулированного пользователя.
        Очистка: удаление всех терминов, созданных этим пользователем.
        """
        for keyword in self.created_keywords[:]:
            try:
                self.client.delete(f"/terms/{keyword}")
            except:
                pass  # Игнорируем ошибки при очистке


class ReadOnlyUser(HttpUser):
    """
    Симулирует пользователя только для чтения, который только читает данные без их изменения.
    Полезно для тестирования read-heavy нагрузок.
    """

    wait_time = between(0.5, 2)

    def on_start(self):
        """Получаем существующие термины для работы с ними."""
        response = self.client.get("/terms")
        if response.status_code == 200:
            terms = response.json()
            self.existing_keywords = [term["keyword"] for term in terms] if terms else []
        else:
            self.existing_keywords = []

    @task(5)
    def list_terms(self):
        """Получение списка всех терминов."""
        response = self.client.get("/terms", name="/terms [LIST] (RO)")
        stats["total_requests"] += 1
        if response.status_code == 200:
            stats["successful_requests"] += 1
        else:
            stats["failed_requests"] += 1

    @task(3)
    def get_random_term(self):
        """Получение конкретного термина."""
        if self.existing_keywords:
            keyword = random.choice(self.existing_keywords)
            response = self.client.get(f"/terms/{keyword}", name="/terms/{keyword} [GET] (RO)")
            stats["total_requests"] += 1
            if response.status_code == 200:
                stats["successful_requests"] += 1
            else:
                stats["failed_requests"] += 1
