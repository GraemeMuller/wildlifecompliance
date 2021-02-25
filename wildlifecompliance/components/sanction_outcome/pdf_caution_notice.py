# -*- coding: utf-8 -*-
import os

from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
# from ledger.payments.pdf import BrokenLine
# from ledger.payments.pdf import BrokenLine
from ledger.payments.pdf import BrokenLine

from wildlifecompliance.doctopdf import create_caution_notice_pdf_contents
from wildlifecompliance.settings import STATIC_ROOT
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, PageBreak, \
    NextPageTemplate, Image
from reportlab.lib.styles import ParagraphStyle, StyleSheet1
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
from reportlab.lib import colors

from django.conf import settings

from wildlifecompliance.components.main.pdf_utils import gap, SolidLine, get_font_str

PAGE_WIDTH, PAGE_HEIGHT = A4
DEFAULT_FONTNAME = 'Helvetica'
BOLD_FONTNAME = 'Helvetica-Bold'

DPAW_HEADER_LOGO = os.path.join(STATIC_ROOT, 'payments', 'img','dbca_logo.jpg')
DPAW_HEADER_LOGO_SM = os.path.join(STATIC_ROOT, 'payments', 'img','dbca_logo_small.png')
BPAY_LOGO = os.path.join(STATIC_ROOT, 'payments', 'img', 'BPAY_2012_PORT_BLUE.png')
HEADER_MARGIN = 10
HEADER_SMALL_BUFFER = 3
PAGE_TOP_MARGIN = 200
VERY_LARGE_FONTSIZE = 14
LARGE_FONTSIZE = 12
MEDIUM_FONTSIZE = 10
SMALL_FONTSIZE = 8
PARAGRAPH_BOTTOM_MARGIN = 5
SECTION_BUFFER_HEIGHT = 10
DATE_FORMAT = '%d/%m/%Y'


def _create_pdf(invoice_buffer, sanction_outcome):
    PAGE_MARGIN = 5 * mm
    page_frame_1 = Frame(PAGE_MARGIN, PAGE_MARGIN, PAGE_WIDTH - 2 * PAGE_MARGIN, PAGE_HEIGHT - 2 * PAGE_MARGIN, id='PagesFrame1', )  #showBoundary=Color(0, 1, 0))
    PAGE_MARGIN2 = 17 * mm
    page_frame_2 = Frame(PAGE_MARGIN2, PAGE_MARGIN2, PAGE_WIDTH - 2 * PAGE_MARGIN2, PAGE_HEIGHT - 2 * PAGE_MARGIN2, id='PagesFrame2', )  #showBoundary=Color(0, 0, 1))
    page_template_1 = PageTemplate(id='Page1', frames=[page_frame_1, ], )
    page_template_2 = PageTemplate(id='Page2', frames=[page_frame_2, ], )
    doc = BaseDocTemplate(invoice_buffer, pageTemplates=[page_template_1, page_template_2], pagesize=A4,)  # showBoundary=Color(1, 0, 0))

    # Common
    FONT_SIZE_L = 11
    FONT_SIZE_M = 10
    FONT_SIZE_S = 8

    styles = StyleSheet1()
    styles.add(ParagraphStyle(name='Normal',
                              fontName='Helvetica',
                              fontSize=FONT_SIZE_M,
                              spaceBefore=7,  # space before paragraph
                              spaceAfter=7,   # space after paragraph
                              leading=12))       # space between lines
    styles.add(ParagraphStyle(name='BodyText',
                              parent=styles['Normal'],
                              spaceBefore=6))
    styles.add(ParagraphStyle(name='Italic',
                              parent=styles['BodyText'],
                              fontName='Helvetica-Italic'))
    styles.add(ParagraphStyle(name='Bold',
                              parent=styles['BodyText'],
                              fontName='Helvetica-Bold',
                              alignment = TA_CENTER))
    styles.add(ParagraphStyle(name='Right',
                              parent=styles['BodyText'],
                              alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='Centre',
                              parent=styles['BodyText'],
                              alignment=TA_CENTER))

    # Logo
    dpaw_header_logo = ImageReader(DPAW_HEADER_LOGO)
    dpaw_header_logo_size = dpaw_header_logo.getSize()
    width = dpaw_header_logo_size[0]/2
    height = dpaw_header_logo_size[1]/2
    dbca_logo = Image(DPAW_HEADER_LOGO, width=width, height=height)

    # Table
    invoice_table_style = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),

        ('SPAN', (0, 0), (1, 0)),

        # Alleged offender
        ('SPAN', (0, 1), (0, 5)),
        ('SPAN', (1, 1), (2, 1)),
        ('SPAN', (1, 2), (2, 2)),
        ('SPAN', (1, 3), (2, 3)),
        ('SPAN', (1, 4), (2, 4)),
        ('SPAN', (1, 5), (2, 5)),

        # When
        ('SPAN', (1, 6), (2, 6)),

        # Where
        ('SPAN', (1, 7), (2, 7)),

        # Alleged offence
        ('SPAN', (0, 8), (0, 9)),
        ('SPAN', (1, 8), (2, 8)),
        # ('SPAN', (1, 9), (2, 9)),
        ('SPAN', (1, 9), (2, 9)),
        # ('SPAN', (1, 10), (2, 10)),

        # Officer issuing notice
        ('SPAN', (0, 10), (0, 12)),
        ('SPAN', (1, 10), (2, 10)),
        ('SPAN', (1, 11), (2, 11)),
        ('SPAN', (1, 12), (2, 12)),

        # Date
        ('SPAN', (1, 13), (2, 13)),

        # Notice to alleged offender
        ('SPAN', (1, 14), (2, 14)),
    ])
    date_str = gap(10) + '/' + gap(10) + '/ 20'
    col_width = [40*mm, 60*mm, 80*mm, ]

    data = []
    data.append([Paragraph('<i>Biodiversity Conservation Act 2016</i><br /><strong><font size="' + str(FONT_SIZE_L) + '">Caution Notice</font></strong>', styles['Normal']),
                 '',
                 Paragraph(u'Caution<br />notice no. ' + get_font_str(sanction_outcome.lodgement_number), styles['Normal'])])

    # Alleged offender
    offender = sanction_outcome.get_offender()
    offender_dob = offender[0].dob.strftime('%d/%m/%Y') if offender[0].dob else ''
    data.append([Paragraph('Alleged offender', styles['Bold']), Paragraph('Name: Family name: ' + get_font_str(offender[0].last_name), styles['Normal']), ''])
    data.append(['', Paragraph(gap(12) + 'Given names: ' + get_font_str(offender[0].first_name), styles['Normal']), ''])
    data.append(['', Paragraph(gap(12) + 'Date of Birth: ' + get_font_str(offender_dob), styles['Normal']), ''])
    data.append(['', [Paragraph('<strong>or</strong><br />Body corporate name', styles['Normal']), Spacer(1, 25)], ''])
    # data.append(['', [Paragraph('Address', styles['Normal']), Spacer(1, 25), Paragraph('Postcode', styles['Normal'])], ''])
    postcode = offender[0].residential_address.postcode if offender[0].residential_address else ''
    data.append(['',
                 [
                     Paragraph('Address: ', styles['Normal']),
                     Paragraph(get_font_str(str(offender[0].residential_address)), styles['Normal']),
                     Paragraph('Postcode: ' + get_font_str(postcode), styles['Normal']),
                 ],
                 '',
                 ])

    # When
    # data.append([Paragraph('When', styles['Bold']), Paragraph('Date' + date_str + gap(5) + 'Time' + gap(10) + 'am/pm', styles['Normal']), ''])
    offence_datetime = sanction_outcome.offence.offence_occurrence_datetime
    data.append([
        Paragraph('When', styles['Bold']),
        Paragraph('Date: ' + get_font_str(offence_datetime.strftime('%d/%m/%Y')) + gap(5) + 'Time: ' + get_font_str(offence_datetime.strftime('%I:%M %p')), styles['Normal']),
        ''
    ])

    # Where
    # data.append([Paragraph('Where', styles['Bold']), [Paragraph('Location of offence', styles['Normal']), Spacer(1, 25)], ''])
    offence_location = sanction_outcome.offence.location
    offence_location_str = str(offence_location) if offence_location else ''
    data.append([
        Paragraph('Where', styles['Bold']),
        [
            Paragraph('Location of offence', styles['Normal']),
            Paragraph(get_font_str(offence_location_str), styles['Normal']),
            Spacer(1, 25)
        ],
        '',
    ])

    # Alleged offence
    data.append([Paragraph('Alleged offence', styles['Bold']),
                 [
                     Paragraph('Description of offence', styles['Normal']),
                 ],
                 ''])  # row index: 8
    # data.append(['', rect, ''])
    # data.append(['', '?', ''])
    data.append(['', Paragraph('<i>Biodiversity Conservation Act 2016 s.</i>' + gap(10) + 'or<br /><i>Biodiversity Conservation Regulations 2018 r.</i>', styles['Normal']), ''])

    # Officer issuing notice
    # data.append([Paragraph('Officer issuing notice', styles['Bold']), Paragraph('Name', styles['Normal']), ''])  # row index: 12
    data.append([
        Paragraph('Officer issuing notice', styles['Bold']),
        Paragraph('Name: {}'.format(get_font_str(sanction_outcome.responsible_officer.get_full_name())), styles['Normal']), ''
    ])  # row index: 12
    data.append(['', Paragraph('Signature', styles['Normal']), ''])
    data.append(['', Paragraph('Officer no.', styles['Normal']), ''])

    # Date
    issue_date = get_font_str(sanction_outcome.date_of_issue.strftime('%d/%m/%Y'))
    issue_time = get_font_str(sanction_outcome.time_of_issue.strftime('%I:%M %p'))
    data.append([Paragraph('Date', styles['Bold']), Paragraph('Date of notice: ' + issue_date + ' ' + issue_time, styles['Normal']), ''])

    # Notice to alleged offender
    body = []
    body.append(Paragraph('It is alleged that you have committed the above offence.</p>', styles['Normal']))
    body.append(Paragraph('If you object to the issue of this notice you can apply in writing to the Approved Officer at the below address for a review within 28 days after the date of this notice.', styles['Normal']))
    body.append(Paragraph('Approved Officer — <i>Biodiversity Conservation Act 2016</i><br />Department of Biodiversity, Conservation and Attractions<br />Locked Bag 104<br />Bentley Delivery Centre WA 6983', styles['Normal']))
    data.append([Paragraph('Notice to alleged offender', styles['Bold']), body, ''])

    # Create 1st table
    t1 = Table(data, style=invoice_table_style, colWidths=col_width)

    # Append tables to the elements to build
    gap_between_tables = 1.5*mm
    elements = []
    elements.append(dbca_logo)
    elements.append(Spacer(0, 5*mm))
    elements.append(t1)
    elements.append(NextPageTemplate(['Page2', ]))
    elements.append(PageBreak())
    elements.append(dbca_logo)
    elements.append(Spacer(0, 5*mm))
    # ORIGINAL NOTES OF INCIDENT:
    title_original_notes = Paragraph('<font size="' + str(FONT_SIZE_L) + '"><strong>ORIGINAL NOTES OF INCIDENT:</strong></font>', styles['Normal'])
    elements.append(title_original_notes)
    elements.append(Spacer(0, 10*mm))
    for i in range(0, 25):
        elements.append(BrokenLine(170*mm, 8*mm))
    elements.append(Paragraph('<font size="' + str(FONT_SIZE_L) + '"><strong>Signature: ' + gap(80) + 'Date:</strong></font>', styles['Normal']))

    doc.build(elements)
    return invoice_buffer


def create_caution_notice_pdf_bytes(filename, sanction_outcome):
    value = create_caution_notice_pdf_contents(filename, sanction_outcome)
    content = ContentFile(value)

    # START: Save the pdf file to the database
    document = sanction_outcome.documents.create(name=filename)
    path = default_storage.save('wildlifecompliance/{}/{}/documents/{}'.format(sanction_outcome._meta.model_name, sanction_outcome.id, filename), content)
    document._file = path
    document.save()
    # END: Save

    return document

    # with BytesIO() as invoice_buffer:
    #     _create_pdf(invoice_buffer, sanction_outcome)
    #
    #     # Get the value of the BytesIO buffer
    #     value = invoice_buffer.getvalue()
    #
    #     # START: Save the pdf file to the database
    #     document = sanction_outcome.documents.create(name=filename)
    #     path = default_storage.save('wildlifecompliance/{}/{}/documents/{}'.format(sanction_outcome._meta.model_name, sanction_outcome.id, filename), invoice_buffer)
    #     document._file = path
    #     document.save()
    #     # END: Save
    #
    #     invoice_buffer.close()
    #
    #     return document


