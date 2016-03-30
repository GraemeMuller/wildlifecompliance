define(
    [
        'jQuery',
        'lodash',
        'js/wl.dataTable',
        'bootstrap'
    ],
    function ($, _, dt) {
        var moduleOptions,
            tableOptions = {
                paging: true,
                info: true,
                searching: true,
                scrollCollapse: true,
                processing: true,
                deferRender: true,
                serverSide: true,
                autowidth: true

            },
            applicationsTable,
            $applicationsLicenceTypeFilter,
            $applicationsStatusTypeFilter;

        function initTables(options) {
            var applicationTableOptions = $.extend({}, tableOptions, {
                    ajax: {
                        url: options.ajax.applications,
                        data: function (d) {
                            // add filters to the query
                            d.filters = $(moduleOptions.selectors.applicationsFilterForm).serializeArray();
                        },
                        error: function () {
                            console.log("error");
                            //TODO Stop the data table 'Processing' and show an error.
                        }
                    }
                }),
                applicationsColumns = [
                    {
                        title: 'Licence Type'
                    },
                    {
                        title: 'Applicant'
                    },
                    {
                        title: 'Status'
                    }
                ];

            applicationsTable = dt.initTable(
                options.selectors.applicationsTable,
                applicationTableOptions,
                applicationsColumns
            );
        }

        function initFilters(options) {
            var data = options.data,
                optionTemplate = _.template('<option value="<%= value %>"><%= title %></option>'),
                $node;

            function createOptionNode(tuple) {
                return $(optionTemplate({
                    value: tuple[0],
                    title: tuple[1] || tuple[0]
                }));
            }

            // applications licence type
            _.forEach(data.applications.filters.licenceType.values, function (value) {

                $node = createOptionNode(value);
                $applicationsLicenceTypeFilter.append($node);
            });
            $applicationsLicenceTypeFilter.on('change', function () {
                applicationsTable.ajax.reload();
            });
            // applications status
            _.forEach(data.applications.filters.status.values, function (value) {
                $node = createOptionNode(value);
                $applicationsStatusTypeFilter.append($node);
            });
            $applicationsStatusTypeFilter.on('change', function () {
                applicationsTable.ajax.reload();
            });

        }

        function setFilters(data) {
            if (data.model) {
                if (data.model === 'application') {
                    $('#applications-collapse').collapse('show');
                    if (data.status) {
                        $applicationsStatusTypeFilter.val(data.status);
                    }
                    if (data.licence_type) {
                        $applicationsLicenceTypeFilter.val(data.licence_type);
                    }
                }
            }
        }

        return function (options) {
            var defaults = {
                selectors: {
                    applicationsTable: '#applications-table',
                    applicationsAccordion: '#applications-collapse',
                    applicationsFilterForm: '#applications-filter-form',
                    applicationsLicenceFilter: '#applications-filter-licence-type',
                    applicationsStatusFilter: '#applications-filter-status'
                },
                ajax: {
                    applications: "/dashboard/data/applications"
                },
                data: {
                    'applications': {
                        'tableData': [],
                        'filters': {
                            'licenceType': {
                                'values': ['All']
                            },
                            'status': {
                                'values': ['All']
                            }
                        }
                    }
                }
            };
            moduleOptions = $.extend({}, defaults, options);
            $(function () {
                $applicationsLicenceTypeFilter = $(moduleOptions.selectors.applicationsLicenceFilter);
                $applicationsStatusTypeFilter = $(moduleOptions.selectors.applicationsStatusFilter);

                $(moduleOptions.selectors.applicationsAccordion).collapse('show');

                initFilters(moduleOptions);
                if (moduleOptions.data.query) {
                    // set filter according to query data
                    setFilters(moduleOptions.data.query);
                }
                initTables(moduleOptions);
            })
        };
    }
);
