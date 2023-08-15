from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    username = models.CharField(
        max_length=150, unique=True, verbose_name="Имя пользователя"
    )
    first_name = models.CharField(max_length=30, verbose_name="Имя")
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username", "first_name", "last_name", "password")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.UniqueConstraint(
                fields=["username", "email"], name="unique_user"
            )
        ]

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Пользователь",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
        help_text="Автор, на которого хочешь подписаться",
    )

    class Meta:
        unique_together = ["user", "author"]

        constraints = (
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_follow"
            ),
            models.CheckConstraint(
                check=~Q(user=F("author")), name="prevent_self_follow"
            ),
        )
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.user.username} подписан на {self.author.username}"
