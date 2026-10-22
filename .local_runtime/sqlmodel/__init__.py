"""Small local SQLModel compatibility layer for running the bundled example offline.

The original project files are untouched. Install the real SQLModel package
when package downloads are available to use the course's intended stack.
"""

from sqlalchemy import UniqueConstraint, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session as _Session, mapped_column


class _Field:
    def __init__(self, default=None, **options):
        self.default = default
        self.options = options


def Field(default=None, **options):
    return _Field(default, **options)


class SQLModel(DeclarativeBase):
    __abstract__ = True

    def __init_subclass__(cls, *, table=False, **kwargs):
        if table:
            annotations = dict(cls.__dict__.get("__annotations__", {}))
            for name, annotation in annotations.items():
                field = cls.__dict__.get(name)
                if isinstance(field, _Field):
                    opts = field.options
                    column_options = {
                        key: opts[key]
                        for key in ("primary_key", "unique", "index")
                        if key in opts
                    }
                    if opts.get("primary_key"):
                        column_options["nullable"] = False
                    if "foreign_key" in opts:
                        from sqlalchemy import ForeignKey

                        args = (ForeignKey(opts["foreign_key"]),)
                    else:
                        args = ()
                    if "default_factory" in opts:
                        column_options["default"] = opts["default_factory"]
                    elif field.default is not None:
                        column_options["default"] = field.default
                    setattr(cls, name, mapped_column(*args, **column_options))
                else:
                    setattr(cls, name, mapped_column())
                annotations[name] = Mapped[annotation]
            cls.__annotations__ = annotations
        super().__init_subclass__(**kwargs)


class Session(_Session):
    def exec(self, statement):
        result = self.execute(statement)
        return result.scalars() if len(statement.column_descriptions) == 1 else result
