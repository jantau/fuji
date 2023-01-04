# -*- coding: utf-8 -*-
# MIT License
#
# Copyright (c) 2020 PANGAEA (https://www.pangaea.de/)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import idutils

from fuji_server.helper.metadata_collector import MetaDataCollector
from fuji_server.helper.request_helper import RequestHelper, AcceptTypes
from fuji_server.helper.metadata_mapper import Mapper
import lxml
import re


class MetaDataCollectorXML(MetaDataCollector):
    """
    A class to collect the  XML metadata given the data. This class is child class of MetadataCollector.

    ...

    Attributes
    ----------
    target_url : str
        Target URL of the metadata
    link_type : str
        Link type of XML

    Methods
    --------
    parse_metadata()
        Method to parse the  XML metadata given the data
    get_mapped_xml_metadata(tree, mapping)
        Get mapped xml metadata

    """
    target_url = None

    def __init__(self, loggerinst, target_url, link_type='embedded', pref_mime_type=None):
        """
        Parameters
        ----------
        mapping : Mapper
            Mapper to metedata sources
        loggerinst : logging.Logger
            Logger instance
        link_type : str, optional
            Link Type, default is 'embedded'
        pref_mime_type : str, optional
            Preferred mime type, e.g. specific XML format
        """
        self.target_url = target_url
        self.link_type = link_type
        self.pref_mime_type = pref_mime_type
        super().__init__(logger=loggerinst)

    def getAllURIs(self, metatree):
        founduris = []
        try:
            #all text element values
            elr = metatree.xpath('//text()')
            for el in elr:
                if str(el).strip():
                    if el not in founduris:
                        if idutils.is_url(el) or idutils.is_urn(el):
                            founduris.append(str(el))
            #all attribute values
            alr = metatree.xpath('//@*')
            for al in alr:
                if al not in founduris:
                    if idutils.is_url(al) or idutils.is_urn(al):
                        founduris.append(str(al))
            founduris =  list(set(founduris))
            #xpath
            # //text()
            # //@*
        except Exception as e:
            print('getAllURIs XML error: '+str(e))
        return founduris

    def parse_metadata(self):
        """Parse the XML metadata from the data.

        Returns
        ------
        str
            a string of source name
        dict
            a dictionary of XML metadata
        """
        xml_metadata = None
        xml_mapping = None
        metatree = None
        envelope_metadata = {}
        self.content_type = 'application/xml'

        XSI = 'http://www.w3.org/2001/XMLSchema-instance'
        if self.link_type == 'linked':
            source_name = self.getEnumSourceNames().TYPED_LINK.value
        if self.link_type == 'embedded':
            source_name = self.getEnumSourceNames().LINKED_DATA.value
        elif self.link_type == 'guessed':
            source_name = self.getEnumSourceNames().GUESSED_XML.value
        elif self.link_type == 'negotiated':
            source_name = self.getEnumSourceNames().XML_NEGOTIATED.value
        else:
            source_name = self.getEnumSourceNames().TYPED_LINK.value
        dc_core_metadata = None
        requestHelper = RequestHelper(self.target_url, self.logger)
        requestHelper.setAcceptType(AcceptTypes.xml)
        requestHelper.setAuthToken(self.auth_token, self.auth_token_type)
        if self.pref_mime_type:
            requestHelper.addAcceptType(self.pref_mime_type)
        #self.logger.info('FsF-F2-01M : Sending request to access metadata from -: {}'.format(self.target_url))
        neg_source, xml_response = requestHelper.content_negotiate('FsF-F2-01M')
        if requestHelper.response_content is not None:
            self.content_type = requestHelper.content_type
            self.logger.info('FsF-F2-01M : Trying to extract/parse XML metadata from URL -: {}'.format(self.target_url))
            #dom = lxml.html.fromstring(self.landing_html.encode('utf8'))
            if neg_source != 'xml':
                self.logger.info('FsF-F2-01M : Expected XML but content negotiation responded -: ' + str(neg_source))
            else:
                try:
                    parser = lxml.etree.XMLParser(strip_cdata=False,recover=True)
                    tree = lxml.etree.XML(xml_response, parser)
                    root_element = tree.tag
                    if root_element.endswith('}OAI-PMH'):
                        self.logger.info(
                            'FsF-F2-01M : Found OAI-PMH type XML envelope, unpacking \'metadata\' element for further processing'
                        )
                        metatree = tree.find('.//{*}metadata/*')
                    elif root_element.endswith('}mets'):
                        self.logger.info(
                            'FsF-F2-01M : Found METS type XML envelope, unpacking all \'xmlData\' elements for further processing'
                        )
                        envelope_metadata = self.get_mapped_xml_metadata(tree, Mapper.XML_MAPPING_METS.value)
                        metatree = tree.find('.//{*}dmdSec/{*}mdWrap/{*}xmlData/*')
                    elif root_element.endswith('}GetRecordsResponse'):
                        self.logger.info(
                            'FsF-F2-01M : Found OGC CSW GetRecords type XML envelope, unpacking \'SearchResults\' element for further processing'
                        )
                        metatree = tree.find('.//{*}SearchResults/*')
                    elif root_element.endswith('}GetRecordByIdResponse'):
                        self.logger.info(
                            'FsF-F2-01M : Found OGC CSW GetRecordByIdResponse type XML envelope, unpacking metadata element for further processing'
                        )
                        metatree = tree.find('.//*')
                    elif root_element.endswith('}DIDL'):
                        self.logger.info(
                            'FsF-F2-01M : Found DIDL (MPEG21) type XML envelope, unpacking metadata element for further processing'
                        )
                        metatree = tree.find('.//{*}Item/{*}Component/{*}Resource/*')
                    else:
                        metatree = tree
                except Exception as e:
                    self.logger.info(
                        'FsF-F2-01M : XML parsing failed -: '+str(e)
                    )
                if metatree is not None:
                    #self.setURIValues(metatree)
                    #print(list(set(self.getURIValues())))

                    self.logger.info(
                        'FsF-F2-01M : Found some XML properties, trying to identify (domain) specific format to parse'
                    )
                    root_namespace = None
                    nsmatch = re.match(r'^\{(.+)\}(.+)$', metatree.tag)
                    schema_locations = set(metatree.xpath('//*/@xsi:schemaLocation', namespaces={'xsi': XSI}))
                    for schema_location in schema_locations:
                        self.namespaces.extend(re.split(r'\s', re.sub(r'\s+', r' ',schema_location)))
                        #self.namespaces = re.split('\s', schema_location)
                    element_namespaces = set(metatree.xpath('//namespace::*'))
                    for el_ns in element_namespaces:
                        if len(el_ns) == 2:
                            if el_ns[1] not in self.namespaces:
                                self.namespaces.append(el_ns[1])
                    if nsmatch:
                        root_namespace = nsmatch[1]
                        root_element = nsmatch[2]
                        #print('#' + root_element + '#', root_namespace)
                        #put the root namespace at the start f list
                        self.namespaces.insert(0,root_namespace)
                    if root_element == 'codeBook':
                        xml_mapping = Mapper.XML_MAPPING_DDI_CODEBOOK.value
                        self.logger.info('FsF-F2-01M : Identified DDI codeBook XML based on root tag')
                    elif root_element == 'StudyUnit':
                        xml_mapping = Mapper.XML_MAPPING_DDI_STUDYUNIT.value
                        self.logger.info('FsF-F2-01M : Identified DDI StudyUnit XML based on root tag')
                    elif root_element == 'CMD':
                        xml_mapping = Mapper.XML_MAPPING_CMD.value
                        self.logger.info('FsF-F2-01M : Identified DDI CMD XML based on root tag')
                    elif root_element == 'DIF':
                        xml_mapping = Mapper.XML_MAPPING_DIF.value
                        self.logger.info('FsF-F2-01M : Identified Directory Interchange Format (DIF) XML based on root tag')
                    elif root_element == 'dc' or any(
                            'http://dublincore.org/schemas/xmls/' in s for s in self.namespaces):
                        xml_mapping = Mapper.XML_MAPPING_DUBLIN_CORE.value
                        self.logger.info('FsF-F2-01M : Identified Dublin Core XML based on root tag or namespace')
                    elif root_element == 'mods':
                        xml_mapping = Mapper.XML_MAPPING_MODS.value
                        self.logger.info('FsF-F2-01M : Identified MODS XML based on root tag')
                    elif root_element == 'eml':
                        xml_mapping = Mapper.XML_MAPPING_EML.value
                        self.logger.info('FsF-F2-01M : Identified EML XML based on root tag')
                    elif root_element in ['MD_Metadata', 'MI_Metadata']:
                        xml_mapping = Mapper.XML_MAPPING_GCMD_ISO.value
                        self.logger.info('FsF-F2-01M : Identified ISO 19115 XML based on root tag')
                    elif root_element == 'rss':
                        self.logger.info('FsF-F2-01M : Identified RSS/GEORSS XML based on root tag')
                    elif root_namespace:
                        if 'datacite.org/schema' in root_namespace:
                            xml_mapping = Mapper.XML_MAPPING_DATACITE.value
                            self.logger.info('FsF-F2-01M : Identified DataCite XML based on namespace')
                    #print('XML Details: ',(self.target_url,root_namespace, root_element))
                    linkeduris = self.getAllURIs(metatree)
                    self.setLinkedNamespaces(linkeduris)
                    if xml_mapping is None:
                        self.logger.info(
                            'FsF-F2-01M : Could not identify (domain) specific XML format to parse'
                        )
                else:
                    self.logger.info(
                        'FsF-F2-01M : Could not find XML properties, could not identify specific XML format to parse'
                    )
        if xml_mapping and metatree is not None:
            xml_metadata = self.get_mapped_xml_metadata(metatree, xml_mapping)

        if envelope_metadata and xml_metadata:
            for envelope_key, envelope_values in envelope_metadata.items():
                if envelope_key not in xml_metadata:
                    xml_metadata[envelope_key] = envelope_values

        #delete empty properties
        if xml_metadata:
            xml_metadata = {k: v for k, v in xml_metadata.items() if v}

        if xml_metadata:
            if requestHelper.checked_content_hash:
                requestHelper.checked_content.get(requestHelper.checked_content_hash)['checked'] = True
            self.logger.info(
                'FsF-F2-01M : Found some metadata in XML -: '+(str(xml_metadata.keys()))
            )
        else:
            self.logger.info('FsF-F2-01M : Could not identify metadata properties in XML')
        return source_name, xml_metadata

    def get_mapped_xml_metadata(self, tree, mapping):
        """Get the mapped XML metadata.

        Parameters
        ----------
        tree
            XML Tree
        mapping
            Mapping object

        Returns
        ------

        dict
            a dictionary of mapped XML metadata
        """
        res = dict()
        #make sure related_resources are not listed in the mapping dict instead related_resource_Reltype has to be used
        res['related_resources'] = []

        for prop in mapping:
            res[prop] = []
            if isinstance(mapping.get(prop).get('path'), list):
                pathlist = mapping.get(prop).get('path')
            else:
                pathlist = [mapping.get(prop).get('path')]

            propcontent = []
            for mappath in pathlist:
                pathdef = mappath.split('@@')
                attribute = None
                if len(pathdef) > 1:
                    attribute = pathdef[1]
                    if ':' in attribute:
                        if attribute.split(':')[0] == 'xlink':
                            attribute = '{http://www.w3.org/1999/xlink}' + attribute.split(':')[1]
                        elif attribute.split(':')[0] == 'xml':
                            attribute = '{http://www.w3.org/XML/1998/namespace}' + attribute.split(':')[1]
                try:
                    subtrees = tree.findall(pathdef[0])
                except Exception as e:
                    print('XML XPATH error ',str(e))
                for subtree in subtrees:
                    propcontent.append({'tree': subtree, 'attribute': attribute})
                    # propcontent.extend({'tree':tree.findall(pathdef[0]),'attribute':attribute})
            if isinstance(propcontent, list):
                if len(propcontent) == 1:
                    if propcontent[0].get('attribute'):
                        res[prop] = propcontent[0].get('tree').attrib.get(propcontent[0].get('attribute'))
                    elif len(propcontent[0].get('tree')) == 0:
                        res[prop] = propcontent[0].get('tree').text
                    else:
                        res[prop] = lxml.etree.tostring(propcontent[0].get('tree'), method='text', encoding='unicode')
                        res[prop] = re.sub('\s+', ' ', res[prop])
                        res[prop] = res[prop].strip()
                else:
                    for propelem in propcontent:
                        if propelem.get('attribute'):
                            res[prop].append(propelem.get('tree').attrib.get(propelem.get('attribute')))
                        elif len(propelem.get('tree')) == 0:
                            res[prop].append(propelem.get('tree').text)
                        else:
                            resprop = lxml.etree.tostring(propelem.get('tree'), method='text', encoding='unicode')
                            resprop = re.sub('\s+', ' ', resprop)
                            resprop = resprop.strip()
                            res[prop].append(resprop)

        #related resources
        for kres, vres in res.items():
            if vres:
                if kres.startswith('related_resource') and 'related_resource_type' not in kres:
                    if isinstance(vres, str):
                        vres = [vres]
                    reltype = kres[17:]
                    if not reltype:
                        reltype = 'related'
                    ri = 0
                    for relres in vres:
                        if relres:
                            if res.get('related_resource_type'):
                                if ri < len(res['related_resource_type']):
                                    reltype = res['related_resource_type'][ri]
                            relres = re.sub(r'[\n\t]*', '', str(relres)).strip()
                        if relres and reltype:
                            res['related_resources'].append({'related_resource': relres, 'resource_type': reltype})
                        ri += 1
        #object_content_identifiers
        '''
        # The code below would theoretically also consider information which does not include a content identifier but only sie or type of content
        res['object_content_identifier'] = []
        if res.get('object_content_identifier_url'):
        #if not isinstance(res.get('object_content_identifier_url'), list):
        #    res['object_content_identifier_url'] = [res.get('object_content_identifier_url')]
        if not isinstance(res.get('object_content_identifier_size'), list):
            res['object_content_identifier_size'] = [res.get('object_content_identifier_size')]
        if not isinstance(res.get('object_content_identifier_type'), list):
            res['object_content_identifier_type'] = [res.get('object_content_identifier_type')]

        object_content_count = max(len(res.get('object_content_identifier_url') or []),
                                      len(res.get('object_content_identifier_type') or []),
                                      len(res.get('object_content_identifier_size') or []))

        for content_index in range(object_content_count):
            try:
                content_url = res['object_content_identifier_url'][content_index]
            except:
                content_url = None
            try:
                content_size = res['object_content_identifier_size'][content_index]
            except:
                content_size = None
            try:
                content_type = res['object_content_identifier_type'][content_index]
            except:
                content_type = None
            res['object_content_identifier'].append({
                'url': content_url,
                'size': content_size,
                'type': content_type
            })
        res.pop('object_content_identifier_type', None)
        res.pop('object_content_identifier_size', None)
        res.pop('object_content_identifier_url', None)
        '''
        if res.get('object_content_identifier_url'):
            res['object_content_identifier'] = []
            if not isinstance(res['object_content_identifier_url'], list):
                res['object_content_identifier_url'] = [res['object_content_identifier_url']]
            ci = 0
            for content_url in res['object_content_identifier_url']:
                content_size = None
                content_type = None
                if res.get('object_content_identifier_size'):
                    if ci < len(res['object_content_identifier_size']):
                        content_size = res['object_content_identifier_size'][ci]
                if res.get('object_content_identifier_type'):
                    if ci < len(res['object_content_identifier_type']):
                        content_type = res['object_content_identifier_type'][ci]
                res['object_content_identifier'].append({
                    'url': content_url,
                    'size': content_size,
                    'type': content_type
                })
                ci += 1
            res.pop('object_content_identifier_type', None)
            res.pop('object_content_identifier_size', None)
            res.pop('object_content_identifier_url', None)
            #print(self.removew(res))
        #print(res)
        return res
