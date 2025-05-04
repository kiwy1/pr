from db import db
from sqlalchemy import Table, Column, Integer, ForeignKey

item_tag = Table(
    "item_tag",
    db.Model.metadata,
    Column("item_id", ForeignKey("items.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True)
)
