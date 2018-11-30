from sqlalchemy import Column, BigInteger, Integer, String

import constants as const


class Users(const.BASE):
    __tablename__ = 'users'

    did = Column(BigInteger, primary_key=True)
    dname = Column(String)
    reactions_triggered = Column(Integer)

    def __str__(self):
        return "ID: {}| Username {}| Reactions triggered: {}" \
            .format(self.did, self.dname, self.reactions_triggered)
