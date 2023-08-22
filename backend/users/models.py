from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q


class User(AbstractUser):
    email = models.EmailField(
        max_length=254, unique=True, verbose_name="Электронная почта"
    )
    username = models.CharField(
        max_length=150, unique=True, verbose_name="Имя пользователя"
    )
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username", "first_name", "last_name", "password")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.UniqueConstraint(
                fields=["username", "email"], name="uq_username_email"
            )
        ]

    def __str__(self) -> str:
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
                fields=["user", "author"], name="uq_user_author"
            ),
            models.CheckConstraint(
                check=~Q(user=F("author")), name="prevent_self_follow"
            ),
        )
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self) -> str:
        return f"{self.user.username} подписан на {self.author.username}"
