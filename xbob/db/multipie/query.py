#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>

"""This module provides the Dataset interface allowing the user to query the
Multi-PIE database in the most obvious ways.
"""

import os
from bob.db import utils
from .models import *
from .driver import Interface

INFO = Interface()

SQLITE_FILE = INFO.files()[0]

class Database(object):
  """The dataset class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """

  def __init__(self):
    # opens a session to the database - keep it open until the end
    self.connect()
    self.s_protocols = ('M', 'U', 'G', 'P051', 'P050', 'P140', 'P041', 'P130', 'P110', 'P240')
    self.s_cameras = ('05_1', '05_0', '14_0', '04_1', '13_0', '11_0', '24_0')
  
  def connect(self):
    """Tries connecting or re-connecting to the database"""
    if not os.path.exists(SQLITE_FILE):
      self.session = None

    else:
      self.session = utils.session(INFO.type(), INFO.files()[0])

  def is_valid(self):
    """Returns if a valid session has been opened for reading the database"""

    return self.session is not None

  def __check_validity__(self, l, obj, valid):
    """Checks validity of user input data against a set of valid values"""
    if not l: return valid
    elif isinstance(l, str): return self.__check_validity__((l,), obj, valid)
    for k in l:
      if k not in valid:
        raise RuntimeError, 'Invalid %s "%s". Valid values are %s, or lists/tuples of those' % (obj, k, valid)
    return l

  def clients(self, protocol=None, groups=None, subworld=None, gender=None, birthyear=None):
    """Returns a set of clients for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('M', 'U', 'G', 'P051', 'P050', 'P140', 'P041', 'P130', 'P110', 'P240')

    groups
      The groups to which the clients belong ('dev', 'eval', 'world')

    subworld
      Specify a split of the world data ("sub41", "sub81", "sub121, "sub161", "")
      In order to be considered, "world" should be in groups.

    gender
      The genders to which the clients belong ('f', 'm')

    birthyear
      The birth year of the clients (in the range [1900,2050])

    Returns: A list containing all the client ids which have the given
    properties.
    """

    VALID_PROTOCOLS = self.s_protocols
    VALID_GROUPS = ('dev', 'eval', 'world')
    VALID_SUBWORLDS = ('sub41', 'sub81', 'sub121', 'sub161')
    VALID_GENDERS = ('m', 'f')
    VALID_BIRTHYEARS = range(1900, 2050)
    VALID_BIRTHYEARS.append(57) # bug in subject_list.txt (57 instead of 1957)
    protocol = self.__check_validity__(protocol, 'protocol', VALID_PROTOCOLS)
    groups = self.__check_validity__(groups, 'group', VALID_GROUPS)
    if subworld: subworld = self.__check_validity__(subworld, 'subworld', VALID_SUBWORLDS)
    gender = self.__check_validity__(gender, 'gender', VALID_GENDERS)
    birthyear = self.__check_validity__(birthyear, 'birthyear', VALID_BIRTHYEARS)
    # List of the clients
    retval = []
    # World data
    if "world" in groups:
      if subworld:
        q = self.session.query(Client).join(SubworldClient).filter(SubworldClient.name.in_(subworld))
      else:
        q = self.session.query(Client)
      q = q.filter(Client.sgroup == 'world').\
            filter(Client.gender.in_(gender)).\
            filter(Client.birthyear.in_(birthyear)).\
            order_by(Client.id)
      for id in [k.id for k in q]:
        retval.append(id)
    # dev / eval data
    if 'dev' in groups or 'eval' in groups:
      q = self.session.query(Client).\
            filter(and_(Client.sgroup != 'world', Client.sgroup.in_(groups))).\
            filter(Client.gender.in_(gender)).\
            filter(Client.birthyear.in_(birthyear)).\
            order_by(Client.id)
      for id in [k.id for k in q]:
        retval.append(id)
    return retval

  def tclients(self, protocol=None, groups=None):
    """Returns a set of T-Norm clients for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('M', 'U', 'G', 'P051', 'P050', 'P140', 'P041', 'P130', 'P110', 'P240')
    
    groups
      The groups to which the clients belong ('dev', 'eval').

    Returns: A list containing all the client ids belonging to the given group.
    """

    VALID_GROUPS = ('dev', 'eval')
    groups = self.__check_validity__(groups, "group", VALID_GROUPS)
    tgroups = []
    if 'dev' in groups:
      tgroups.append('eval')
    if 'eval' in groups:
      tgroups.append('dev')
    return self.clients(protocol, tgroups)

  def zclients(self, protocol=None, groups=None):
    """Returns a set of Z-Norm clients for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('M', 'U', 'G', 'P051', 'P050', 'P140', 'P041', 'P130', 'P110', 'P240')
    
    groups
      The groups to which the clients belong ('dev', 'eval').

    Returns: A list containing all the client ids belonging to the given group.
    """

    VALID_GROUPS = ('dev', 'eval')
    groups = self.__check_validity__(groups, "group", VALID_GROUPS)
    zgroups = []
    if 'dev' in groups:
      zgroups.append('eval')
    if 'eval' in groups:
      zgroups.append('dev')
    return self.clients(protocol, zgroups)

  def models(self, protocol=None, groups=None):
    """Returns a set of models for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('M', 'U', 'G', 'P051', 'P050', 'P140', 'P041', 'P130', 'P110', 'P240')
    
    groups
      The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')

    Returns: A list containing all the model ids belonging to the given group.
    """

    return self.clients(protocol, groups)

  def tmodels(self, protocol=None, groups=None):
    """Returns a set of T-Norm models for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('M', 'U', 'G', 'P051', 'P050', 'P140', 'P041', 'P130', 'P110', 'P240')
    
    groups
      The groups to which the models belong ('dev', 'eval').

    Returns: A list containing all the model ids belonging to the given group.
    """

    return self.tclients(protocol, groups)

  def zmodels(self, protocol=None, groups=None):
    """Returns a set of Z-Norm models for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('M', 'U', 'G', 'P051', 'P050', 'P140', 'P041', 'P130', 'P110', 'P240')
    
    groups
      The groups to which the models belong ('dev', 'eval').

    Returns: A list containing all the model ids belonging to the given group.
    """

    return self.zclients(protocol, groups)


  def get_client_id_from_model_id(self, model_id):
    """Returns the client_id attached to the given model_id
    
    Keyword Parameters:

    model_id
      The model_id to consider

    Returns: The client_id attached to the given model_id
    """
    return model_id

  def get_client_id_from_tmodel_id(self, model_id):
    """Returns the client_id attached to the given T-Norm model_id
    
    Keyword Parameters:

    model_id
      The model_id to consider

    Returns: The client_id attached to the given T-Norm model_id
    """
    return model_id

  def get_client_id_from_file_id(self, file_id):
    """Returns the client_id (real client id) attached to the given file_id
    
    Keyword Parameters:

    file_id
      The file_id to consider

    Returns: The client_id attached to the given file_id
    """
    q = self.session.query(File).\
          filter(File.id == file_id)
    if q.count() !=1:
      #throw exception?
      return None
    else:
      return q.first().client_id

  def get_internal_path_from_file_id(self, file_id):
    """Returns the unique "internal path" attached to the given file_id
    
    Keyword Parameters:

    file_id
      The file_id to consider

    Returns: The internal path attached to the given file_id
    """
    q = self.session.query(File).\
          filter(File.id == file_id)
    if q.count() !=1:
      #throw exception?
      return None
    else:
      return q.first().path


  def objects(self, directory=None, extension=None, protocol=None,
      purposes=None, model_ids=None, groups=None, classes=None, subworld=None,
      expressions=None, world_cameras=None, world_sampling=1, world_noflash=False, 
      world_first=False, world_second=False, world_third=False, world_fourth=False,
      world_nshots=None, world_shots=None):
    """Returns a set of filenames for the specific query by the user.

    Keyword Parameters:

    directory
      A directory name that will be prepended to the final filepath returned

    extension
      A filename extension that will be appended to the final filepath returned

    protocol
      One of the Multi-PIE protocols ('M', 'U', 'G', 'P051', 'P050', 'P140', 'P041', 'P130', 'P110', 'P240').

    purposes
      The purposes required to be retrieved ('enrol', 'probe') or a tuple
      with several of them. If 'None' is given (this is the default), it is 
      considered the same as a tuple with all possible values. This field is
      ignored for the data from the "world" group.

    model_ids
      Only retrieves the files for the provided list of model ids (claimed 
      client id).  If 'None' is given (this is the default), no filter over 
      the model_ids is performed.

    groups
      One of the groups ('dev', 'eval', 'world') or a tuple with several of them. 
      If 'None' is given (this is the default), it is considered the same as a 
      tuple with all possible values.

    classes
      The classes (types of accesses) to be retrieved ('client', 'impostor') 
      or a tuple with several of them. If 'None' is given (this is the 
      default), it is considered the same as a tuple with all possible values.
  
    subworld
      Specify a split of the world data ("sub41", "sub81", "sub121, "sub161", "")
      In order to be considered, "world" should be in groups.

    expressions
      The (face) expressions to be retrieved ('neutral', 'smile', 'surprise',
      'squint', 'disgust', 'scream') or a tuple with several of them. 
      If 'None' is given (this is the default), it is considered the same as 
      a tuple with all possible values.

    world_cameras
      The cameras to be retrieved ('05_1', '05_0', '14_0', '04_1', '13_0',
      '11_0', '24_0') or a tuple with several of them. 
      If 'None' is given (this is the default), it is considered the same as 
      a tuple with all possible values. The world_camera keyword is ignored in 
      the 'dev' and 'eval' sets.  

    world_sampling
      Samples the files from the world data set. Keeps only files such as::
      
        File.client_id + File.shot_id % world_sampling == 0

      This argument should be an integer between 1 (keep everything) and 19.
      It is not used if world_noflash is also set.

    world_nshots
      Only considers the n first shots from the world data set.

    world_shots
      Only considers the shots with the given ids.

    world_noflash
      Keeps the files from the world dataset recorded without flash (shot 0)
      
    world_first
      Only uses data from the first recorded session of each user of the world
      dataset.

    world_second
      Only uses data from the second recorded session of each user of the world
      dataset.

    world_third
      Only uses data from the third recorded session of each user of the world
      dataset.

    world_fourth
      Only uses data from the fourth recorded session of each user of the world
      dataset.

    Returns: A dictionary containing the resolved filenames considering all
    the filtering criteria. The keys of the dictionary are unique identities 
    for each file in the Multi-PIE database. Conserve these numbers if you 
    wish to save processing results later on.
    """

    def make_path(stem, directory, extension):
      import os
      if not extension: extension = ''
      if directory: return os.path.join(directory, stem + extension)
      return stem + extension

    VALID_PROTOCOLS = self.s_protocols
    VALID_PURPOSES = ('enrol', 'probe')
    VALID_GROUPS = ('dev', 'eval', 'world')
    VALID_CLASSES = ('client', 'impostor')
    VALID_SUBWORLDS = ('sub41', 'sub81', 'sub121', 'sub161')
    VALID_EXPRESSIONS = ('neutral', 'smile', 'surprise', 'squint', 'disgust', 'scream')
    VALID_CAMERAS = self.s_cameras

    protocol = self.__check_validity__(protocol, 'protocol', VALID_PROTOCOLS)
    purposes = self.__check_validity__(purposes, 'purpose', VALID_PURPOSES)
    groups = self.__check_validity__(groups, 'group', VALID_GROUPS)
    classes = self.__check_validity__(classes, 'class', VALID_CLASSES)
    if subworld: subworld = self.__check_validity__(subworld, 'subworld', VALID_SUBWORLDS)
    expressions = self.__check_validity__(expressions, 'expression', VALID_EXPRESSIONS)
    world_cameras = self.__check_validity__(world_cameras, 'camera', VALID_CAMERAS)

    retval = {}
    
    if(isinstance(model_ids,str)):
      model_ids = (model_ids,)
   
    if 'world' in groups:
      # Multiview
      """
      q = self.session.query(File,Expression).join(Client).join(FileMultiview).\
            filter(Client.sgroup == 'world').\
            filter(Expression.name.in_(expressions)).\
            filter(and_(File.img_type == 'multiview', File.session_id == Expression.session_id,\
                        File.recording_id == Expression.recording_id, FileMultiview.shot_id != 19))
      """
      q = self.session.query(FileProtocol).join(File).join(Client).join(ProtocolName).join(FileMultiview).\
            filter(and_(ProtocolName.name.in_(protocol), FileMultiview.camera_id.in_(world_cameras), Client.sgroup == 'world', FileProtocol.purpose == 'world'))
      if subworld:
        q = q.join(SubworldClient).filter(SubworldClient.name.in_(subworld))
      if model_ids:
        q = q.filter(File.client_id.in_(model_ids))
      if(world_nshots):
        max1 = 19
        max2 = 19
        max3 = 19
        max4 = 19
        if world_nshots < 19:
          max1 = world_nshots
          max2 = 0
          max3 = 0
          max4 = 0
        elif world_nshots < 38:
          max2 = world_nshots - 19
          max3 = 0
          max4 = 0
        elif world_nshots < 57:
          max3 = world_nshots - 38
          max4 = 0
        else:
          max4 = world_nshots - 57
        q = q.filter(or_( and_( File.session_id == Client.first_session, or_(and_(File.recording_id == 1, FileMultiview.shot_id < max1),
                                                                             and_(File.recording_id == 2, FileMultiview.shot_id < max2))),
                          and_( File.session_id == Client.second_session, or_(and_(File.recording_id == 1, FileMultiview.shot_id < max2),
                                                                              and_(File.recording_id == 2, FileMultiview.shot_id < max3))),
                          and_( File.session_id == Client.third_session, or_(and_(File.recording_id == 1, FileMultiview.shot_id < max3),
                                                                             and_(File.recording_id == 2, FileMultiview.shot_id < max4))),
                          and_( File.session_id == Client.fourth_session, FileMultiview.shot_id < max4)))
      if(world_shots):
        q = q.filter(FileMultiview.shot_id.in_(world_shots))
      if( world_sampling != 1 and world_noflash == False):
        q = q.filter(((File.client_id + FileMultiview.shot_id) % world_sampling) == 0)
      if( world_noflash == True):
        q = q.filter(FileMultiview.shot_id == 0)
      if( world_first == True):
        q = q.filter(and_(File.session_id == Client.first_session, or_(Client.first_session != 4, 
                  and_(Client.first_session == 4, File.recording_id == 1))))
      if( world_second == True):
        q = q.filter(or_( and_(Client.second_session != 4, File.session_id == Client.second_session),
                          or_( and_(Client.first_session == 4, and_(File.session_id == 4, File.recording_id == 2)),
                               and_(Client.second_session == 4, and_(File.session_id == 4, File.recording_id == 1)))))
      if( world_third == True):
        q = q.filter(or_( and_(Client.third_session != 4, File.session_id == Client.third_session),
                          or_( and_(Client.second_session == 4, and_(File.session_id == 4, File.recording_id == 2)),
                               and_(Client.third_session == 4, and_(File.session_id == 4, File.recording_id == 1)))))
      if( world_fourth == True):
        q = q.filter(or_( and_(Client.fourth_session != 4, File.session_id == Client.fourth_session),
                          or_( and_(Client.third_session == 4, and_(File.session_id == 4, File.recording_id == 2)),
                               and_(Client.fourth_session == 4, and_(File.session_id == 4, File.recording_id == 1)))))
      for k in q:
        kk = k.file
        retval[kk.id] = (make_path(kk.path, directory, extension), kk.client_id, kk.client_id, kk.client_id, kk.path)
    
      # Highres
      # TODO

    if('dev' in groups or 'eval' in groups): 
      # Dev and/or eval groups from the query
      groups_de = []
      if 'dev' in groups: groups_de.append('dev')
      if 'eval' in groups: groups_de.append('eval')

      # Multiview
      # Enrol
      if('enrol' in purposes):
        q = self.session.query(FileProtocol).join(File).join(Client).join(ProtocolName).\
              filter(and_(ProtocolName.name.in_(protocol), Client.sgroup.in_(groups_de), FileProtocol.purpose == 'enrol'))
        if model_ids:
          q = q.filter(and_(Client.id.in_(model_ids)))
        for k in q:
          kk = k.file
          retval[kk.id] = (make_path(kk.path, directory, extension), kk.client_id, kk.client_id, kk.client_id, kk.path)
      # Probe
      if('probe' in purposes):
        # Note: defining the variable q once outside the if statement makes it less efficient!
        if('client' in classes and 'impostor' in classes):
          q = self.session.query(FileProtocol).join(File).join(Client).join(ProtocolName).\
                filter(and_(ProtocolName.name.in_(protocol), Client.sgroup.in_(groups_de), FileProtocol.purpose == 'probe'))
          for k in q: 
            kk = k.file
            if(model_ids and len(model_ids) == 1):
              retval[kk.id] = (make_path(kk.path, directory, extension), model_ids[0], model_ids[0], kk.client_id, kk.path)
            else:
              retval[kk.id] = (make_path(kk.path, directory, extension), kk.client_id, kk.client_id, kk.client_id, kk.path)
        elif('client' in classes):
          q = self.session.query(FileProtocol).join(File).join(Client).join(ProtocolName).\
                filter(and_(ProtocolName.name.in_(protocol), Client.sgroup.in_(groups_de), FileProtocol.purpose == 'probe'))
          if model_ids:
            q = q.filter(Client.id.in_(model_ids))
          for k in q: 
            kk = k.file
            retval[kk.id] = (make_path(kk.path, directory, extension), kk.client_id, kk.client_id, kk.client_id, kk.path) 
        elif('impostor' in classes):
          q = self.session.query(FileProtocol).join(File).join(Client).join(ProtocolName).\
                filter(and_(ProtocolName.name.in_(protocol), Client.sgroup.in_(groups_de), FileProtocol.purpose == 'probe'))
          if(model_ids and len(model_ids)==1):
            q = q.filter(not_(Client.id.in_(model_ids)))
          for k in q:
            kk = k.file
            if(model_ids and len(model_ids) == 1):
              retval[kk.id] = (make_path(kk.path, directory, extension), model_ids[0], model_ids[0], kk.client_id, kk.path)
            else:
              retval[kk.id] = (make_path(kk.path, directory, extension), kk.client_id, kk.client_id, kk.client_id, kk.path)

      # Highres
      # TODO

    return retval

  def files(self, directory=None, extension=None, protocol=None,
      purposes=None, model_ids=None, groups=None, classes=None, subworld=None,
      expressions=None, world_cameras=None, world_sampling=1, world_noflash=False, 
      world_first=False, world_second=False, world_third=False, world_fourth=False,
      world_nshots=None, world_shots=None):
    """Returns a set of filenames for the specific query by the user.

    Keyword Parameters:

    directory
      A directory name that will be prepended to the final filepath returned

    extension
      A filename extension that will be appended to the final filepath returned

    protocol
      One of the Multi-PIE protocols ('M', 'U', 'G', 'P051', 'P050', 'P140', 'P041', 'P130', 'P110', 'P240').

    purposes
      The purposes required to be retrieved ('enrol', 'probe') or a tuple
      with several of them. If 'None' is given (this is the default), it is 
      considered the same as a tuple with all possible values. This field is
      ignored for the data from the 'world' group.

    model_ids
      Only retrieves the files for the provided list of model ids (claimed 
      client id).  If 'None' is given (this is the default), no filter over 
      the model_ids is performed.

    groups
      One of the groups ('dev', 'eval', 'world') or a tuple with several of them. 
      If 'None' is given (this is the default), it is considered the same as a 
      tuple with all possible values.

    classes
      The classes (types of accesses) to be retrieved ('client', 'impostor') 
      or a tuple with several of them. If 'None' is given (this is the 
      default), it is considered the same as a tuple with all possible values.

    subworld
      Specify a split of the world data ("sub41", "sub81", "sub121, "sub161", "")
      In order to be considered, "world" should be in groups.

    expressions
      The (face) expressions to be retrieved ('neutral', 'smile', 'surprise',
      'squint', 'disgust', 'scream') or a tuple with several of them. 
      If 'None' is given (this is the default), it is considered the same as 
      a tuple with all possible values.

    world_cameras
      The cameras to be retrieved ('05_1', '05_0', '14_0', '04_1', '13_0',
      '11_0', '24_0') or a tuple with several of them. 
      If 'None' is given (this is the default), it is considered the same as 
      a tuple with all possible values. The world_camera keyword is ignored in 
      the 'dev' and 'eval' sets.  

    world_sampling
      Samples the files from the world data set. Keeps only files such as::

        File.client_id + File.shot_id % world_sampling == 0

      This argument should be an integer between 1 (keep everything) and 20.
      It is not used if world_noflash is also set.

    world_nshots
      Only considers the n first shots from the world data set.

    world_shots
      Only considers the shots with the given ids.

    world_noflash
      Keeps the files from the world dataset recorded without flash (shot 0)
      
    world_first
      Only uses data from the first recorded session of each user of the world
      dataset.

    world_second
      Only uses data from the second recorded session of each user of the world
      dataset.

    world_third
      Only uses data from the third recorded session of each user of the world
      dataset.

    world_fourth
      Only uses data from the fourth recorded session of each user of the world
      dataset.

    Returns: A dictionary containing the resolved filenames considering all
    the filtering criteria. The keys of the dictionary are unique identities 
    for each file in the Multi-PIE database. Conserve these numbers if you 
    wish to save processing results later on.
    """

    retval = {}
    d = self.objects(directory, extension, protocol, purposes, model_ids, groups, classes, subworld, expressions, world_cameras, world_sampling, world_noflash, world_first, world_second, world_third, world_fourth, world_nshots, world_shots)
    for k in d: retval[k] = d[k][0]

    return retval


  def tobjects(self, directory=None, extension=None, protocol=None,
      model_ids=None, groups=None, expressions=None):
    """Returns a set of filenames for enrolling T-norm models for score 
       normalization.

    Keyword Parameters:

    directory
      A directory name that will be prepended to the final filepath returned

    extension
      A filename extension that will be appended to the final filepath returned

    protocol
      One of the Multi-PIE protocols ('M', 'U', 'G', 'P051', 'P050', 'P140', 'P041', 'P130', 'P110', 'P240').

    model_ids
      Only retrieves the files for the provided list of model ids (claimed 
      client id).  If 'None' is given (this is the default), no filter over 
      the model_ids is performed.

    groups
      The groups to which the clients belong ('dev', 'eval').

    expressions
      The (face) expressions to be retrieved ('neutral', 'smile', 'surprise',
      'squint', 'disgust', 'scream') or a tuple with several of them. 
      If 'None' is given (this is the default), it is considered the same as 
      a tuple with all possible values.

    Returns: A dictionary containing:
      - 0: the resolved filenames 
      - 1: the model id
      - 2: the claimed id attached to the model
      - 3: the real id
      - 4: the "stem" path (basename of the file)

    considering all the filtering criteria. The keys of the dictionary are 
    unique identities for each file in the Multi-PIE database. Conserve these 
    numbers if you wish to save processing results later on.
    """

    VALID_GROUPS = ('dev', 'eval')
    groups = self.__check_validity__(groups, "group", VALID_GROUPS)
    tgroups = []
    if 'dev' in groups:
      tgroups.append('eval')
    if 'eval' in groups:
      tgroups.append('dev')
    return self.objects(directory, extension, protocol, 'enrol', model_ids, tgroups, 'client', None, expressions)

  def tfiles(self, directory=None, extension=None, protocol=None,
      model_ids=None, groups=None, expressions=None):
    """Returns a set of filenames for enrolling T-norm models for score 
       normalization.

    Keyword Parameters:

    directory
      A directory name that will be prepended to the final filepath returned

    extension
      A filename extension that will be appended to the final filepath returned

    protocol
      One of the Multi-PIE protocols ('M', 'U', 'G', 'P051', 'P050', 'P140', 'P041', 'P130', 'P110', 'P240').

    model_ids
      Only retrieves the files for the provided list of model ids (claimed 
      client id).  If 'None' is given (this is the default), no filter over 
      the model_ids is performed.

    groups
      The groups to which the clients belong ('dev', 'eval').

    expressions
      The (face) expressions to be retrieved ('neutral', 'smile', 'surprise',
      'squint', 'disgust', 'scream') or a tuple with several of them. 
      If 'None' is given (this is the default), it is considered the same as 
      a tuple with all possible values.

    Returns: A dictionary containing:
      - 0: the resolved filenames 
      - 1: the model id
      - 2: the claimed id attached to the model
      - 3: the real id
      - 4: the "stem" path (basename of the file)

    considering allthe filtering criteria. The keys of the dictionary are 
    unique identities for each file in the Multi-PIE database. Conserve these 
    numbers if you wish to save processing results later on.
    """

    retval = {}
    d = self.tobjects(directory, extension, protocol, model_ids, groups, expressions)
    for k in d: retval[k] = d[k][0]

    return retval

  def zobjects(self, directory=None, extension=None, protocol=None,
      model_ids=None, groups=None, expressions=None):
    """Returns a set of filenames of impostors for Z-norm score normalization.

    Keyword Parameters:

    directory
      A directory name that will be prepended to the final filepath returned

    extension
      A filename extension that will be appended to the final filepath returned

    protocol
      One of the Multi-PIE protocols ('M', 'U', 'G', 'P051', 'P050', 'P140', 'P041', 'P130', 'P110', 'P240').

    model_ids
      Only retrieves the files for the provided list of model ids (client id).  
      If 'None' is given (this is the default), no filter over the model_ids 
      is performed.

    groups
      The groups to which the clients belong ('dev', 'eval').

    expressions
      The (face) expressions to be retrieved ('neutral', 'smile', 'surprise',
      'squint', 'disgust', 'scream') or a tuple with several of them. 
      If 'None' is given (this is the default), it is considered the same as 
      a tuple with all possible values.

    Returns: A dictionary containing:
      - 0: the resolved filenames 
      - 1: the client id
      - 2: the "stem" path (basename of the file)

    considering allthe filtering criteria. The keys of the dictionary are 
    unique identities for each file in the Multi-PIE database. Conserve these
    numbers if you wish to save processing results later on.
    """

    VALID_GROUPS = ('dev', 'eval')
    groups = self.__check_validity__(groups, "group", VALID_GROUPS)

    zgroups = []
    if 'dev' in groups:
      zgroups.append('eval')
    if 'eval' in groups:
      zgroups.append('dev')

    retval = {}
    d = self.objects(directory, extension, protocol, 'probe', model_ids, zgroups, 'client', None, expressions)
    for k in d: retval[k] = d[k]

    return retval

  def zfiles(self, directory=None, extension=None, protocol=None,
      model_ids=None, groups=None, expressions=None):
    """Returns a set of filenames for enrolling T-norm models for score 
       normalization.

    Keyword Parameters:

    directory
      A directory name that will be prepended to the final filepath returned

    extension
      A filename extension that will be appended to the final filepath returned

    protocol
      One of the Multi-PIE protocols ('M', 'U', 'G', 'P051', 'P050', 'P140', 'P041', 'P130', 'P110', 'P240').

    model_ids
      Only retrieves the files for the provided list of model ids (claimed 
      client id).  If 'None' is given (this is the default), no filter over 
      the model_ids is performed.

    groups
      The groups to which the clients belong ('dev', 'eval').

    expressions
      The (face) expressions to be retrieved ('neutral', 'smile', 'surprise',
      'squint', 'disgust', 'scream') or a tuple with several of them. 
      If 'None' is given (this is the default), it is considered the same as 
      a tuple with all possible values.

    Returns: A dictionary containing:
      - 0: the resolved filenames 
      - 1: the client id
      - 2: the "stem" path (basename of the file)

    considering allthe filtering criteria. The keys of the dictionary are 
    unique identities for each file in the Multi-PIE database. Conserve these 
    numbers if you wish to save processing results later on.
    """

    retval = {}
    d = self.zobjects(directory, extension, protocol, model_ids, groups, expressions)
    for k in d: retval[k] = d[k][0]

    return retval


  def save_one(self, id, obj, directory, extension):
    """Saves a single object supporting the bob save() protocol.

    This method will call save() on the the given object using the correct
    database filename stem for the given id.
    
    Keyword Parameters:

    id
      The id of the object in the database table "file".

    obj
      The object that needs to be saved, respecting the bob save() protocol.

    directory
      This is the base directory to which you want to save the data. The
      directory is tested for existence and created if it is not there with
      os.makedirs()

    extension
      The extension determines the way each of the arrays will be saved.
    """

    import os
    from bob.io import save

    fobj = self.session.query(File).filter_by(id=id).one()
    fullpath = os.path.join(directory, str(fobj.path) + extension)
    fulldir = os.path.dirname(fullpath)
    utils.makedirs_safe(fulldir)
    save(obj, fullpath)

  def save(self, data, directory, extension):
    """This method takes a dictionary of blitz arrays or bob.database.Array's
    and saves the data respecting the original arrangement as returned by
    files().

    Keyword Parameters:

    data
      A dictionary with two keys 'real' and 'attack', each containing a
      dictionary mapping file ids from the original database to an object that
      supports the bob "save()" protocol.

    directory
      This is the base directory to which you want to save the data. The
      directory is tested for existence and created if it is not there with
      os.makedirs()

    extension
      The extension determines the way each of the arrays will be saved.
    """    

    for key, value in data:
      self.save_one(key, value, directory, extension)
