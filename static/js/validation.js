class EmployeeFormValidator {
    constructor(formSelector) {
        this.form = $(formSelector);
        this.fields = {
            'first_name': {
                selector: '#first-name',
                errorSelector: '#first-name-error',
                minLength: 2,
                maxLength: 50,
                required: true,
                pattern: /^[a-zA-Z\s'-]+$/,
                patternMessage: 'First name can only contain letters, spaces, hyphens, and apostrophes.'
            },
            'last_name': {
                selector: '#last-name',
                errorSelector: '#last-name-error',
                minLength: 2,
                maxLength: 50,
                required: true,
                pattern: /^[a-zA-Z\s'-]+$/,
                patternMessage: 'Last name can only contain letters, spaces, hyphens, and apostrophes.'
            },
            'employee_id': {
                selector: '#employee-id',
                errorSelector: '#employee-id-error',
                minLength: 3,
                maxLength: 20,
                required: true,
                pattern: /^[A-Z0-9]+$/,
                patternMessage: 'Employee ID must contain only uppercase letters and numbers.'
            },
            'department': {
                selector: '#department',
                errorSelector: '#department-error',
                required: true
            },
            'employment_status': {
                selector: '#employment-status',
                errorSelector: '#employment-status-error',
                required: true
            }
        };
        
        this.debounceTimers = {};
    }

    init() {
        this.bindEvents();
        this.setupFieldValidation();
    }

    bindEvents() {
        this.form.on('submit', (e) => this.handleSubmit(e));
        
        Object.keys(this.fields).forEach(fieldName => {
            const field = this.fields[fieldName];
            $(field.selector).on('blur', () => this.validateField(fieldName));
            $(field.selector).on('input change', () => this.clearFieldError(fieldName));
        });
    }

    setupFieldValidation() {
        $('#employee-id').on('input', function() {
            $(this).val($(this).val().toUpperCase().replace(/[^A-Z0-9]/g, ''));
        });

        $('#first-name, #last-name').on('input', function() {
            $(this).val($(this).val().replace(/[^a-zA-Z\s'-]/g, ''));
        });
    }

    handleSubmit(e) {
        let isValid = true;
        const firstInvalidField = null;

        Object.keys(this.fields).forEach(fieldName => {
            if (!this.validateField(fieldName)) {
                isValid = false;
                if (!firstInvalidField) {
                    firstInvalidField = fieldName;
                }
            }
        });

        if (!isValid) {
            e.preventDefault();
            const firstInvalidSelector = this.fields[firstInvalidField].selector;
            $(firstInvalidSelector).trigger('focus');
            return false;
        }

        $('#save-employee').prop('disabled', true).html(
            '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Saving...'
        );

        return true;
    }

    validateField(fieldName) {
        const field = this.fields[fieldName];
        const $input = $(field.selector);
        const value = $input.val().trim();
        let isValid = true;
        let errorMessage = '';

        $input.removeClass('is-invalid is-valid');
        $(field.errorSelector).text('').hide();

        if (field.required && !value) {
            isValid = false;
            errorMessage = this.getFieldLabel(fieldName) + ' is required.';
        } else if (value) {
            if (field.minLength && value.length < field.minLength) {
                isValid = false;
                errorMessage = this.getFieldLabel(fieldName) + ' must be at least ' + field.minLength + ' characters long.';
            } else if (field.maxLength && value.length > field.maxLength) {
                isValid = false;
                errorMessage = this.getFieldLabel(fieldName) + ' cannot exceed ' + field.maxLength + ' characters.';
            } else if (field.pattern && !field.pattern.test(value)) {
                isValid = false;
                errorMessage = field.patternMessage;
            }
        }

        if (isValid && value) {
            $input.addClass('is-valid');
        } else if (!isValid) {
            $input.addClass('is-invalid');
            $(field.errorSelector).text(errorMessage).show();
        }

        return isValid;
    }

    clearFieldError(fieldName) {
        const field = this.fields[fieldName];
        const $input = $(field.selector);
        
        if ($input.hasClass('is-invalid')) {
            this.validateField(fieldName);
        }
    }

    getFieldLabel(fieldName) {
        const labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'employee_id': 'Employee ID',
            'department': 'Department',
            'employment_status': 'Employment Status'
        };
        return labels[fieldName] || fieldName;
    }

    showServerErrors(errors) {
        Object.keys(errors).forEach(fieldName => {
            if (this.fields[fieldName]) {
                const field = this.fields[fieldName];
                const $input = $(field.selector);
                const errorMsg = errors[fieldName];
                
                $input.addClass('is-invalid').removeClass('is-valid');
                $(field.errorSelector).text(errorMsg).show();
            }
        });
    }

    resetForm() {
        this.form[0].reset();
        Object.keys(this.fields).forEach(fieldName => {
            const field = this.fields[fieldName];
            $(field.selector).removeClass('is-invalid is-valid');
            $(field.errorSelector).text('').hide();
        });
    }
}

function showToast(message, type = 'info') {
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    let $container = $('.toast-container');
    if (!$container.length) {
        $container = $('<div class="toast-container position-fixed bottom-0 end-0 p-3"></div>');
        $('body').append($container);
    }
    
    const $toast = $(toastHtml);
    $container.append($toast);
    const toast = new bootstrap.Toast($toast[0], { delay: 5000 });
    toast.show();
    
    $toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

$(document).ready(function() {
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    $('[data-bs-toggle="popover"]').popover();
    
    $('.alert-dismissible').on('close.bs.alert', function() {
        $(this).addClass('fade');
    });
    
    $('#employee-search').on('input', function() {
        clearTimeout($(this).data('searchTimer'));
        const $input = $(this);
        $input.data('searchTimer', setTimeout(function() {
            // Auto-search could be implemented here
        }, 300));
    });
    
    $(document).ajaxStart(function() {
        $('body').addClass('loading');
    }).ajaxStop(function() {
        $('body').removeClass('loading');
    });
});