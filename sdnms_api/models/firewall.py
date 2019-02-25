import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

SAModel = declarative_base()


class FirewallAddressModel(SAModel):
    __tablename__ = 'firewall_address'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(255), nullable=False, unique=True)
    addrtype = sa.Column(sa.String(128), nullable=False)
    content = sa.Column(sa.String(255), nullable=False)
    interface = sa.Column(sa.String(15), nullable=False)
    comments = sa.Column(sa.Text)

    def __init__(self, name, addrtype, content, interface, comments):
        self.name = name
        self.addrtype = addrtype
        self.content = content
        self.interface = interface
        self.comments = comments

    @property
    def as_dict(self):
        return {
            'name': self.name,
            'address type': self.addrtype,
            'content': self.content,
            'interface': self.interface,
            'comment': self.comment
        }

    @classmethod
    def get_list(cls, session):
        with session.begin():
            query = session.query(cls)
            models = query.all()

        return models

    @classmethod
    def get(cls, session, id):
        with session.begin():
            query = session.query(cls)
            model = query.filter(cls.id == id).one()

        return model

    def save(self, session):
        with session.begin():
            session.add(self)

    def delete(self, session):
        with session.begin():
            session.delete(self)


class FirewallServiceModel(SAModel):
    __tablename__ = 'firewall_service'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(255), nullable=False)
    protocol_type = sa.Column(sa.String(15), nullable=False)
    comment = sa.Column(sa.Text)
    # TCP/UDP/SCTP
    address = sa.Column(sa.String(128))
    dest_port = sa.Column(sa.SmallInteger, default=1)
    dest_port_low = sa.Column(sa.Integer)
    dest_port_high = sa.Column(sa.Integer)
    # ICMP
    icmp_type = sa.Column(sa.String(128))
    code = sa.Column(sa.String(128))
    # IP
    protocol_number = sa.Column(sa.String(128))

    def __init__(self, name, protocol_type, address, dest_port, dest_port_low, dest_port_high,
                 icmp_type, code, protocol_number, comment):
        self.name = name
        self.protocol_type = protocol_type
        self.address = address
        self.dest_port = dest_port
        self.dest_port_low = dest_port_low
        self.dest_port_high = dest_port_high
        self.icmp_type = icmp_type
        self.code = code
        self.protocol_number = protocol_number
        self.comment = comment

    # used display to user view
    def get_dest_port_display(self, flag):
        if flag == 1:
            return "TCP"
        elif flag == 2:
            return "UDP"
        else:
            return "SCTP"

    @property
    def as_dict(self):
        return {
            'name': self.name,
            'protocol_type': self.protocol_type,
            'address': self.address,
            'dest_port': self.dest_port,
            'dest_port_low': self.dest_port_low,
            'dest_port_high': self.dest_port_high,
            'type': self.type,
            'code': self.code,
            'protocol_number': self.protocol_number,
            'comment': self.comment
        }

    def save(self, session):
        with session.begin():
            session.add(self)

    @classmethod
    def get_list(cls, session):
        models = []

        with session.begin():
            query = session.query(cls)
            models = query.all()

        return models


class FirewallPolicyModel(SAModel):
    __tablename__ = 'firewall_policy'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(255), nullable=False)
    incoming_interface = sa.Column(sa.SmallInteger, nullable=False)
    outgoing_interface = sa.Column(sa.SmallInteger, nullable=False)
    source = sa.Column(sa.ForeignKey('firewall_address.id'), nullable=False)
    destination = sa.Column(sa.ForeignKey('firewall_address.id'), nullable=False)
    schedule = sa.Column(sa.String(128), default="always")
    services = sa.Column(sa.ForeignKey('firewall_service.id'))
    action = sa.Column(sa.SmallInteger, default=1)
    nat = sa.Column(sa.SmallInteger, default=1)
    status = sa.Column(sa.SmallInteger, default=1)
    comment = sa.Column(sa.Text)

    def __init__(self, name, incoming_interface, outgoing_interface, source, destination, schedule,
                 services, action, nat, comment, status):
        self.name = name
        self.incoming_interface = incoming_interface
        self.outgoing_interface = outgoing_interface
        self.source = source
        self.destination = destination
        self.schedule = schedule
        self.services = services
        self.action = action
        self.nat = nat
        self.comment = comment
        self.status = status

    # used display to user view
    def get_action_display(self, flag):
        if flag == 1:
            return "Accept"
        else:
            return "Deny"

    # used display to user view
    def get_nat_display(self, flag):
        if flag == 1:
            return "Enable"
        else:
            return "Disable"

    # used display to user view
    def get_status_display(self, flag):
        if flag == 1:
            return "Enable"
        else:
            return "Disable"

    # used display to user view
    def get_interface_display(self, number):
        return "port{0}".format(number)

    @property
    def as_dict(self):
        return {
            'name': self.name,
            'incoming_interface': self.incoming_interface,
            'outgoing_interface': self.outgoing_interface,
            'source': self.source,
            'destination': self.destination,
            'schedule': self.schedule,
            'services': self.services,
            'action': self.action,
            'nat': self.nat,
            'comment': self.comment,
            'status': self.status
        }

    def save(self, session):
        with session.begin():
            session.add(self)

    @classmethod
    def get_list(cls, session):
        models = []

        with session.begin():
            query = session.query(cls)
            models = query.all()

        return models