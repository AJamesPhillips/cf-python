import cfdm

from .constants import cr_coordinates, cr_canonical_units, cr_default_values
from .functions import RTOL, ATOL, allclose
from .functions import inspect as cf_inspect
from .query     import Query

from . import CoordinateConversion
from . import Datum

from .data.data import Data

from .functions import (_DEPRECATION_ERROR_METHOD,
                        _DEPRECATION_ERROR_ATTRIBUTE,
                        )

_units = {}


class CoordinateReference(cfdm.CoordinateReference):
    '''A coordinate reference construct of the CF data model. 

    A coordinate reference construct relates the coordinate values of
    the coordinate system to locations in a planetary reference frame.
    
    The domain of a field construct may contain various coordinate
    systems, each of which is constructed from a subset of the
    dimension and auxiliary coordinate constructs. For example, the
    domain of a four-dimensional field construct may contain
    horizontal (y-x), vertical (z), and temporal (t) coordinate
    systems. There may be more than one of each of these, if there is
    more than one coordinate construct applying to a particular
    spatiotemporal dimension (for example, there could be both
    latitude-longitude and y-x projection coordinate systems). In
    general, a coordinate system may be constructed implicitly from
    any subset of the coordinate constructs, yet a coordinate
    construct does not need to be explicitly or exclusively associated
    with any coordinate system.
    
    A coordinate system of the field construct can be explicitly
    defined by a coordinate reference construct which relates the
    coordinate values of the coordinate system to locations in a
    planetary reference frame and consists of the following:
    
    * References to the dimension coordinate and auxiliary coordinate
      constructs that define the coordinate system to which the
      coordinate reference construct applies. Note that the coordinate
      values are not relevant to the coordinate reference construct,
      only their properties.
    
    ..
    
    * A definition of a datum specifying the zeroes of the dimension
      and auxiliary coordinate constructs which define the coordinate
      system. The datum may be implied by the metadata of the
      referenced dimension and auxiliary coordinate constructs, or
      explicitly provided.
    
    ..
    
    * A coordinate conversion, which defines a formula for converting
      coordinate values taken from the dimension or auxiliary
      coordinate constructs to a different coordinate system. A
      coordinate reference construct relates the coordinate values of
      the field to locations in a planetary reference frame.
    
    
    **NetCDF interface**
    
    The netCDF grid mapping variable name of a coordinate reference
    construct may be accessed with the `nc_set_variable`,
    `nc_get_variable`, `nc_del_variable` and `nc_has_variable`
    methods.

    '''
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance._CoordinateConversion = CoordinateConversion
        instance._Datum                = Datum
        return instance


    def __getitem__(self, key):
        '''Return a parameter value of the datum or the coordinate conversion.

    x.__getitem__(key) <==> x[key]
    
    If the same parameter exists in both the datum and the coordinate
    conversion then an exception is raised.
    
    .. seealso:: `get`, `coordinate_conversion.get_parameter`,
                 `datum.get_parameter`

        '''
        out = []
        try:
            out.append(self.coordinate_conversion.get_parameter(key))
        except ValueError:
            try:
                out.append(self.datum.get_parameter(key))
            except ValueError:
                pass
        #--- End: try
        
        if len(out) == 1:
            return out[0]

        if not out:
            raise KeyError(
                "No {!r} parameter exists in the coordinate conversion nor the datum".format(
                    key))

        raise KeyError(
            "{!r} parameter exists in both the coordinate conversion and the datum".format(
                key))


    def __hash__(self):
        '''x.__hash__() <==> hash(x)

        '''
#        if self.type == 'formula_terms':
#            raise ValueError("Can't hash a formula_terms %s" %
#                             self.__class__.__name__)

        h = sorted(self.items())# TODO
        h.append(self.identity())

        return hash(tuple(h))


    def __repr__(self): 
        '''Called by the `repr` built-in function. 

    x.__repr__() <==> repr(x)

        ''' 
        return super().__repr__().replace('<', '<CF ', 1)


    # ----------------------------------------------------------------
    # Private methods
    # ----------------------------------------------------------------
    def _matching_values(self, value0, value1):
        '''TODO
        '''
        if isinstance(value0, Query):
            return bool(value0.evaluate(value1)) # TODO vectors

        try:
            # re.compile object
            return value0.search(value1)
        except (AttributeError, TypeError):
            return self._equals(value1, value0)

    
    # ----------------------------------------------------------------
    # Private attributes
    # ----------------------------------------------------------------
    @property
    def _coordinate_identities(self):
        '''TODO

    .. versionadded:: 3.0.0

        '''
        return cr_coordinates.get(self.identity(), ())

        
    def has_bounds(self):
        '''Returns False since coordinate reference constructs do not have cell bounds.

    **Examples:**

    >>> c.has_bounds()
    False

        '''
        return False


#    def canonical(self, field=None):
#        '''
#'''
#        ref = self.copy()
#
#        for term, value in ref.parameters.iteritems():
#            if value is None or isinstance(value, str):
#                continue
#
#            canonical_units = self.canonical_units(term)
#            if canonical_units is None:
#                continue
#
#            if isinstance(canonical_units, str):
#                # units is a standard_name of a coordinate
#                if field is None:
#                    raise ValueError("Set the field parameter")
#                coord = field.coord(canonical_units, exact=True)
#                if coord is not None:
#                    canonical_units = coord.Units
#
#            if canonical_units is not None:
#                units = getattr(value, 'Units', None)
#                if units is not None:
#                    if not canonical_units.equivalent(units):
#                        raise ValueError("xasdddddddddddddd 87236768 TODO")                
#                    value.Units = canonical_units
#        #--- End: for
#
#        return ref


    @classmethod
    def canonical_units(cls, term):
        '''Return the canonical units for a standard CF coordinate conversion
    term.

    :Parameters:
    
        term: `str`
            The name of the term.
    
    :Returns:
    
        `Units` or `None`
            The canonical units, or `None` if there are not any.
    
    **Examples:**
    
    >>> cf.CoordinateReference.canonical_units('perspective_point_height')
    <Units: m>
    >>> cf.CoordinateReference.canonical_units('ptop')
    None

        '''
        return cr_canonical_units.get(term, None)


    def close(self):
        '''Close all files referenced by coordinate conversion term values.

    :Returns:
    
        `None`
    
    **Examples:**
    
    >>> c.close()

        '''
        pass


    @classmethod
    def default_value(cls, term):
        '''Return the default value for an unset standard CF coordinate
    conversion term.
    
    :Parameters:	
    
        term: `str`
            The name of the term.
    
    :Returns:	
    
            The default value, or 0.0 if one is not available.
    
    **Examples:**
    
    >>> cf.CoordinateReference.default_value('ptop')
    0.0
    >>> print cf.CoordinateReference.default_value('north_pole_grid_latitude')
    0.0

        '''
        return cr_default_values.get(term, 0.0)

    
    def equivalent(self, other, atol=None, rtol=None, verbose=False,
                   traceback=False):
        '''True if two coordinate references are logically equal, False
    otherwise.
    
    :Parameters:
    
        other: cf.CoordinateReference
            The object to compare for equality.
    
        atol: `float`, optional
            The absolute tolerance for all numerical comparisons, By
            default the value returned by the `cf.ATOL` function is used.
    
        rtol: `float`, optional
            The relative tolerance for all numerical comparisons, By
            default the value returned by the `cf.RTOL` function is used.
    
        traceback: `bool`, optional
            If True then print a traceback highlighting where the two
            instances differ. TODO
    
    :Returns:
    
        out: `bool`
            Whether or not the two objects are equivalent.
    
    **Examples:**
    
    TODO

        '''
        if traceback:
            _DEPRECATION_ERROR_KWRAGS(self, 'equivalent', traceback=True) # pragma: no cover
        
        if self is other:
            return True
        
        # Check that each instance is the same type
        if self.__class__ != other.__class__:
            if verbose:
                print("{}: Different types ({!r} != {!r})".format(
                    self.__class__.__name__,
                    self.__class__.__name__, other.__class__.__name__)) # pragma: no cover
            return False
   
        # ------------------------------------------------------------
        # Check the name
        # ------------------------------------------------------------
        if self.identity() != other.identity():
            if verbose:
                print("{}: Different identities ({!r} != {!r})".format(
                    self.__class__.__name__, self.identity(), other.identity())) # pragma: no cover
            return False
                
        # ------------------------------------------------------------
        # Check the domain ancillary terms
        # ------------------------------------------------------------
#        ancillaries0 = self._conversion['ancillary']
#        ancillaries1 = other._conversion['ancillary']
        ancillaries0 = self.coordinate_conversion.domain_ancillaries()
        ancillaries1 = other.coordinate_conversion.domain_ancillaries()
        if set(ancillaries0) != set(ancillaries1):
            if verbose:
                print("{}: Non-equivalent domain ancillary terms".format(
                    self.__class__.__name__)) # pragma: no cover
            return False
            
        # Check that if one term is None then so is the other
        for term, value0 in ancillaries0.items():
            if (value0 is None) != (ancillaries1[term] is None):
                if verbose:
                    print(
                        "{}: Non-equivalent domain ancillary-valued term {!r}".format(
                            self.__class__.__name__,  term)) # pragma: no cover
                return False
        #--- End: for

        # ------------------------------------------------------------
        # Check the parameter terms and their values
        # ------------------------------------------------------------
        if rtol is None:
            rtol = RTOL()
        if atol is None:
            atol = ATOL()

#        parameters0 = self._conversion['parameter']
#        parameters1 = other._conversion['parameter']
        parameters0 = self.coordinate_conversion.parameters()
        parameters1 = other.coordinate_conversion.parameters()

        for term in set(parameters0).union(parameters1):
            value0 = parameters0.get(term, None)
            value1 = parameters1.get(term, None)

            if value1 is None and value0 is None:
                # Term is unset in self and other
                continue

            if value0 is None:
                # Term is unset in self
                value0 = self.default_value(term)

            if value1 is None:
                # Term is unset in other
               value1 = other.default_value(term)

            if not allclose(value0, value1, rtol=rtol, atol=atol):
                if verbose:
                    print("{}: Non-equivalent coordinate conversion parameter-valued term {!r}".format(
                        self.__class__.__name__,  term)) # pragma: no cover
                return False
        #--- End: for

        parameters0 = self.datum.parameters()
        parameters1 = other.datum.parameters()

        for term in set(parameters0).union(parameters1):
            value0 = parameters0.get(term, None)
            value1 = parameters1.get(term, None)

            if value1 is None and value0 is None:
                # Term is unset in self and other
                continue

            if value0 is None:
                # Term is unset in self
                value0 = self.default_value(term)

            if value1 is None:
                # Term is unset in other
               value1 = other.default_value(term)

            if not allclose(value0, value1, rtol=rtol, atol=atol):
                if verbose:
                    print("{}: Non-equivalent datum parameter-valued term {!r}".format(
                        self.__class__.__name__,  term)) # pragma: no cover
                return False
        #--- End: for

       # Still here?
        return True


    def get(self, key, default=None):
        '''Return a parameter value of the datum or the coordinate conversion.

    .. versionadded:: 3.0.0
    
    .. seealso:: `coordinate_conversion.get_parameter`,
                 `datum.get_parameter`, `__getitem__`,
    
    :Parameters:
    
        key: `str` TODO
    
        default: optional TODO
    
    :Returns:
    
            The parameter value.

        '''
        try:
            return self[key]
        except KeyError:
            return default


    def inspect(self):
        '''Inspect the attributes.

    .. seealso:: `cf.inspect`
    
    :Returns: 
    
        `None`

        '''
        print(cf_inspect(self)) # pragma: no cover

        
    def match_by_identity(self, *identities):
        '''Determine whether or not one of the identities matches.

    .. versionadded:: 3.0.0
    
    .. seealso:: `identities`, `match`
    
    :Parameters:
    
        TODO
    
    :Returns:
    
        `bool`
            Whether or not the coordinate reference matches one of the
            given identities.
    
    **Examples:**

    TODO

        '''
        if not identities:
            return True

        self_identities = self.identities()

        x = self.coordinate_conversion.get_parameter('grid_mapping_name', None)
        if x is not None:
            self_identities.append(x)
        
        x = self.coordinate_conversion.get_parameter('standard_name', None)
        if x is not None:
            self_identities.append(x)
 
        ok = False
        for value0 in identities:          
            for value1 in self_identities:
                ok = self._matching_values(value0, value1)
                if ok:
                    break
            #--- End: for

            if ok:
                break
        #--- End: for

        return ok


    def match(self, *identities):
        '''Alias for `cf.CoordinateReference.match_by_identity`

        '''
        return self.match_by_identity(*identities)


    def change_identifiers(self, identity_map, coordinate=True,
                           ancillary=True, strict=False,
                           inplace=False, i=False):
        '''Change the TODO

    ntifier is not in the provided mapping then it is
    set to `None` and thus effectively removed from the coordinate
    reference.
    
    :Parameters:
    
        identity_map: dict
            For example: ``{'dim2': 'dim3', 'aux2': 'latitude', 'aux4': None}``
            
        strict: `bool`, optional
            If True then coordinate or domain ancillary identifiers not
            set in the *identity_map* dictiontary are set to `None`. By
            default they are left unchanged.
    
        i: `bool`, optional
    
    :Returns:
    
        `None`
    
    **Examples:**
    
    >>> r = cf.CoordinateReference('atmosphere_hybrid_height_coordinate',
    ...                             a='ncvar:ak',
    ...                             b='ncvar:bk')
    >>> r.coordinates
    {'atmosphere_hybrid_height_coordinate'}
    >>> r.change_coord_identitiers({'atmosphere_hybrid_height_coordinate', 'dim1',
    ...                             'ncvar:ak': 'aux0'})
    >>> r.coordinates
    {'dim1', 'aux0'}

        '''
     
        if i:
            _DEPRECATION_ERROR_KWRAGS(self, 'change_identifiers', i=True) # pragma: no cover

        if inplace:
            r = self
        else:
            r = self.copy()

        if not identity_map and not strict:
            if inplace:
                r = None            
            return r

        if strict:
            default = None

        if ancillary:
            for term, identifier in r.coordinate_conversion.domain_ancillaries().items():
                if not strict:
                    default = identifier
                r.coordinate_conversion.set_domain_ancillary(term, identity_map.get(identifier, default), copy=False)        
        #--- End: if

        if coordinate:
            for identifier in r.coordinates():
                if not strict:
                    default = identifier
                    
                r.del_coordinate(identifier)
                r.set_coordinate(identity_map.get(identifier, default))            
        #--- End: if

        r.del_coordinate(None, None)
        
        if inplace:
            r = None            
        return r


    def structural_signature(self, rtol=None, atol=None):
        '''TODO

    :Return:

        `tuple`
        '''     
        s = [self.identity()]
        append = s.append


        for component in ('datum', 'coordinate_conversion'):
            x = getattr(self, component)
            for term, value in sorted(x.parameters().items()):
                if isinstance(value, str):
                    append((component+':'+term, value))
                    continue
                    
                if value is None:
                    # Do not add an unset scalar or vector parameter value
                    # to the structural signature
                    continue
    
                value = Data.asdata(value, dtype=float)
    
                cu = self.canonical_units(term)
                if cu is not None:
                    if value.Units.equivalent(cu):
                        value.Units = cu
                    elif value.Units:
                        cu = value.Units
                else:
                    cu = value.Units
    
                if str(cu) in _units:
                    cu = _units[str(cu)]
                else:    
                    ok = 0
                    for units in _units.values():
                        if cu.equals(units):
                            _units[str(cu)] = units
                            cu = units
                            ok = 1
                            break
                    if not ok:
                        _units[str(cu)] = cu 
    
                if allclose(value, self.default_value(term), rtol=rtol, atol=atol):
                    # Do not add a default value to the structural signature
                    continue
                
                append((component+':'+term, value, cu.formatted(definition=True)))
        #--- End: for                

        # Add the domain ancillary-valued terms which have been set
        append(tuple(sorted([term for term, value in self.coordinate_conversion.domain_ancillaries().items()
                             if value is not None])))

        return tuple(s)


    # ----------------------------------------------------------------
    # Deprecated attributes and methods
    # ----------------------------------------------------------------
    def __delitem__(self, key):
        '''x.__delitem__(key) <==> del x[key]

    Deprecated at version 3.0.0. Use method 'datum.del_parameter',
    'coordinate_conversion.del_parameter' or
    'coordinate_conversion.del_domain_ancillary' instead.

        '''
        _DEPRECATION_ERROR_METHOD(self, '__getitem__',
                                  "Use method 'datum.del_parameter', 'coordinate_conversion.del_parameter' or 'coordinate_conversion.del_domain_ancillary' instead.") # pragma: no cover


    @property
    def conversion(self):
        '''Deprecated at version 3.0.0. Use attribute 'coordinate_conversion'
    instead.

        '''
        _DEPRECATION_ERROR_ATTRIBUTE(
            self, 'conversion', 
            "Use attribute 'coordinate_conversion' instead.") # pragma: no cover

    
    @property
    def hasbounds(self):
        '''False. Coordinate reference objects do not have cell bounds.

    Deprecated at version 3.0.0. Use method 'has_bounds' instead.

        '''
        _DEPRECATION_ERROR_ATTRIBUTE(
            self, 'hasbounds',
            "Use method 'has_bounds' instead.") # pragma: no cover


    @property
    def ancillaries(self):
        '''Deprecated at version 3.0.0. Use the
    'coordinate_conversion.domain_ancillaries' method instead.

        '''
        _DEPRECATION_ERROR_ATTRIBUTE(
            self, 'ancillaries',
            "Use the 'coordinate_conversion.domain_ancillaries' method instead.") # pragma: no cover


    @property
    def parameters(self):
        '''Deprecated at version 3.0.0. Use methods
    'coordinate_conversion.parameters' and 'c.datum.parameters'
    instead.

        '''
        _DEPRECATION_ERROR_ATTRIBUTE(
            self, 'parameters',
            "Use methods 'coordinate_conversion.parameters' and 'datum.parameters' instead.") # pragma: no cover


    def clear(self, coordinates=True, parameters=True, ancillaries=True):
        '''Deprecated at version 3.0.0. Use methods
    'coordinate_conversion.parameters' and 'datum.parameters' instead.

        '''
        _DEPRECATION_ERROR_METHOD(
            self, 'parameters',
            "Use methods 'coordinate_conversion.parameters' and 'datum.parameters' instead.") # pragma: no cover


    def name(self, default=None, identity=False, ncvar=False):
        '''Return a name.

    Deprecated at version 3.0.0. Use the 'identity' method instead.
        '''
        _DEPRECATION_ERROR_METHOD(self, 'name', "Use the 'identity' method instead.") # pragma: no cover


    def all_identifiers(self):
        '''Deprecated at version 3.0.0.

        '''
        _DEPRECATION_ERROR_METHOD(self, 'all_identifiers') # pragma: no cover


    def set_term(self, term_type, term, value):
        '''Deprecated at version 3.0.0. Use method 'datum.set_parameter',
    'coordinate_conversion.set_parameter' or
    'coordinate_conversion.set_domain_ancillary' instead.

        '''
        _DEPRECATION_ERROR_METHOD(
            self, 'set_term', 
            "Use method 'datum.set_parameter', 'coordinate_conversion.set_parameter' or 'coordinate_conversion.set_domain_ancillary' instead.") # pragma: no cover


#--- End: class

