"""
Конфигурация нагрузочного тестирования Locust для API глоссария.

Этот файл определяет поведение пользователей для нагрузочного тестирования FastAPI приложения.
Запуск: locust -f locustfile.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between
import random
import string


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
        self.client.get("/terms", name="/terms [LIST]")

    @task(8)
    def get_random_term(self):
        """
        Получение конкретного термина по keyword.
        Вес: 8
        """
        if self.existing_keywords:
            keyword = random.choice(self.existing_keywords)
            self.client.get(f"/terms/{keyword}", name="/terms/{keyword} [GET]")
        else:
            # Если терминов нет, получим 404
            self.client.get("/terms/nonexistent", name="/terms/{keyword} [GET 404]")

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

        if response.status_code == 201:
            self.created_keywords.append(keyword)
            self.existing_keywords.append(keyword)

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

            self.client.put(
                f"/terms/{keyword}",
                json=payload,
                name="/terms/{keyword} [UPDATE]"
            )

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

            if response.status_code == 204:
                # Удаляем также из списка существующих keywords
                if keyword in self.existing_keywords:
                    self.existing_keywords.remove(keyword)

    @task(1)
    def get_nonexistent_term(self):
        """
        Намеренная попытка получить несуществующий термин для тестирования обработки ошибок.
        Вес: 1
        """
        fake_keyword = self._generate_random_keyword()
        self.client.get(
            f"/terms/{fake_keyword}",
            name="/terms/{keyword} [GET 404]"
        )

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
        self.client.get("/terms", name="/terms [LIST]")

    @task(3)
    def get_random_term(self):
        """Получение конкретного термина."""
        if self.existing_keywords:
            keyword = random.choice(self.existing_keywords)
            self.client.get(f"/terms/{keyword}", name="/terms/{keyword} [GET]")
